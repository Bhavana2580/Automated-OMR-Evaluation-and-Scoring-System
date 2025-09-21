# backend/omr/processor.py

import cv2
import numpy as np
import json
import os
import tempfile
from .utils import load_image, to_grayscale, save_image
from .pdf_utils import pdf_to_images

class OMRProcessor:
    def __init__(self, templates_dir=None, answer_key_path=None):
        base = os.path.dirname(__file__)
        self.templates_dir = templates_dir or os.path.join(base, "templates")
        # If sample data includes an answer_keys.json, pass path in
        self.answer_keys = self._load_answer_keys(answer_key_path)
    
    def _load_answer_keys(self, answer_key_path):
        # priority: provided path, then sample_data folder, then templates
        if answer_key_path and os.path.exists(answer_key_path):
            with open(answer_key_path, 'r') as f:
                return json.load(f)
        # default sample_data/answer_keys.json relative to project root
        default_path = os.path.join(os.path.dirname(base:=os.path.dirname(__file__)), "sample_data", "answer_keys.json")
        if os.path.exists(default_path):
            with open(default_path, 'r') as f:
                return json.load(f)
        # fallback: template in templates
        template_k = os.path.join(self.templates_dir, "template_v1.json")
        if os.path.exists(template_k):
            with open(template_k, 'r') as f:
                templ = json.load(f)
                # if template has "answer_key" field
                if "answer_key" in templ:
                    return { templ.get("meta", {}).get("version", "v1") : templ["answer_key"] }
        # fallback demo
        return { "v1": ["A"]*20 + ["B"]*20 + ["C"]*20 + ["D"]*20 + ["A"]*20 }
    
    def process(self, file_path: str, version: str = "v1", student_id: str = None):
        """
        Accepts an image or PDF. If PDF, converts to images and processes first page (or all pages).
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        image_paths = []
        if ext == ".pdf":
            # convert
            tmpdir = tempfile.mkdtemp(prefix="omr_pdf_")
            image_paths = pdf_to_images(file_path, tmpdir)
            if not image_paths:
                raise ValueError("PDF conversion failed or produced no images")
        else:
            image_paths = [file_path]
        
        # process the first image (or optionally all pages)
        results = []
        for img_path in image_paths:
            try:
                res = self.process_image(img_path, version, student_id=student_id)
            except Exception as e:
                # log error, but continue with other pages or bubble up
                raise
        
            results.append(res)
            # if just single sheet per student, break
            break
        
        # return first result
        return results[0]
    
    def process_image(self, img_path, version='v1', student_id: str = None):
        """
        Main image → answers pipeline. Returns dict with
        total_score, section_scores, raw answers, overlay etc.
        """
        img = load_image(img_path)
        if img is None:
            raise ValueError(f"Unable to read image from {img_path}")
        
        # Preprocessing:
        gray = to_grayscale(img)
        # maybe apply histogram equalization if lighting uneven
        gray = cv2.equalizeHist(gray)
        blurred = cv2.GaussianBlur(gray, (5,5), 0)
        edged = cv2.Canny(blurred, 50, 150)
        
        # Find contour of sheet
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            raise ValueError("No contours found in image")
        
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        sheet_cnt = None
        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4:
                sheet_cnt = approx
                break
        
        if sheet_cnt is None:
            # fallback: use full image corners
            h, w = img.shape[:2]
            sheet_cnt = np.array([[[0,0]], [[w-1,0]], [[w-1,h-1]], [[0,h-1]]])
        
        warped = self._four_point_transform(img, sheet_cnt.reshape(4,2))
        warped_gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        
        # optional: resize to standard size for bubble detection
        # e.g. limit max dimension
        max_dim = 2000
        h2, w2 = warped_gray.shape
        scale = min(max_dim / max(h2,w2), 1.0)
        if scale < 1.0:
            warped_gray = cv2.resize(warped_gray, (int(w2*scale), int(h2*scale)))
            warped = cv2.resize(warped, (int(w2*scale), int(h2*scale)))
        
        # Thresholding
        thresh = cv2.adaptiveThreshold(warped_gray, 255,
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 25, 10)
        
        # Find bubbles
        bubbles = self._find_bubbles(thresh)
        
        answers, overlay = self._extract_answers(warped, thresh, bubbles)
        
        # Scoring
        if version not in self.answer_keys:
            raise ValueError(f"Unknown version '{version}' in answer_keys")
        answer_key = self.answer_keys[version]
        
        if len(answer_key) < 100:
            raise ValueError(f"Answer key for version '{version}' must have 100 entries (found {len(answer_key)})")
        
        section_scores = {}
        total = 0
        for s in range(5):
            start = s * 20
            end = start + 20
            score = 0
            for i in range(start, end):
                pred = answers.get(i+1)
                if pred is not None and pred == answer_key[i]:
                    score += 1
            section_scores[f"subject_{s+1}"] = score
            total += score
        
        overlay_path = os.path.splitext(img_path)[0] + "_overlay.png"
        save_image(overlay_path, overlay)
        
        return {
            "student_id": student_id,
            "version": version,
            "total_score": total,
            "section_scores": section_scores,
            "answers": answers,
            "overlay_path": overlay_path
        }
    
    def _four_point_transform(self, image, pts):
        rect = self._order_points(pts)
        (tl, tr, br, bl) = rect
        widthA = np.linalg.norm(br - bl)
        widthB = np.linalg.norm(tr - tl)
        maxWidth = int(max(widthA, widthB))
        
        heightA = np.linalg.norm(tr - br)
        heightB = np.linalg.norm(tl - bl)
        maxHeight = int(max(heightA, heightB))
        
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]
        ], dtype = "float32")
        
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        return warped
    
    def _order_points(self, pts):
        rect = np.zeros((4,2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        
        return rect
    
    def _find_bubbles(self, thresh_img):
        cnts, _ = cv2.findContours(thresh_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        bubble_contours = []
        for c in cnts:
            (x, y, w, h) = cv2.boundingRect(c)
            ar = w / float(h) if h != 0 else 0
            area = cv2.contourArea(c)
            # Heuristics: aspect ratio near 1, size reasonable relative to sheet
            if 15 < w < 100 and 15 < h < 100 and 0.7 <= ar <= 1.3 and area > 100:
                bubble_contours.append((x, y, w, h, c))
        bubble_contours = sorted(bubble_contours, key=lambda b: (b[1], b[0]))
        return bubble_contours
    
    def _extract_answers(self, warped_color, thresh, bubble_contours):
        answers = {}
        overlay = warped_color.copy()
        
        centers = []
        for (x, y, w, h, c) in bubble_contours:
            cx = x + w/2
            cy = y + h/2
            centers.append(((cx, cy), (x, y, w, h)))
        if not centers:
            return answers, overlay
        
        centers_sorted = sorted(centers, key=lambda x: (x[0][1], x[0][0]))
        
        rows = []
        current_row = [centers_sorted[0]]
        row_y = centers_sorted[0][0][1]
        for center in centers_sorted[1:]:
            if abs(center[0][1] - row_y) < 25:  # row threshold
                current_row.append(center)
            else:
                rows.append(current_row)
                current_row = [center]
                row_y = center[0][1]
        rows.append(current_row)
        
        # sort each row by x
        for i in range(len(rows)):
            rows[i] = sorted(rows[i], key=lambda x: x[0][0])
        
        qnum = 1
        for r in rows:
            # process groups of 5 (choices A-E) in each row
            for i in range(0, len(r), 5):
                group = r[i:i+5]
                if len(group) != 5:
                    continue
                fill_scores = []
                for (cxcy, bbox) in group:
                    (x, y, w, h) = bbox
                    # pad a little inside bbox for ROI
                    pad = int(min(w, h) * 0.1)
                    x0 = int(x + pad)
                    y0 = int(y + pad)
                    x1 = int(x + w - pad)
                    y1 = int(y + h - pad)
                    roi = thresh[y0:y1, x0:x1]
                    if roi.size == 0:
                        fill_scores.append(0)
                    else:
                        fill_scores.append(np.count_nonzero(roi) / float(roi.size))
                chosen_idx = int(np.argmax(fill_scores))
                chosen_score = fill_scores[chosen_idx]
                # threshold for marking
                if chosen_score > 0.15:
                    answers[qnum] = ['A','B','C','D','E'][chosen_idx]
                    # draw overlay circle
                    cx, cy = int(group[chosen_idx][0][0]), int(group[chosen_idx][0][1])
                    cv2.circle(overlay, (cx, cy), 15, (0,255,0), 2)
                else:
                    answers[qnum] = None
                qnum += 1
                if qnum > 100:
                    break
            if qnum > 100:
                break
        
        return answers, overlay

# backend/omr/classifier.py

"""
classifier.py
Lightweight ML classifier to decide if a bubble is "filled" or "empty".

Usage:
    clf = BubbleClassifier()
    clf.train(train_images, train_labels)   # optional if you have data
    pred = clf.predict(cropped_roi)         # returns 1 if filled, 0 if empty
"""

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import cv2

class BubbleClassifier:
    def _init_(self, model=None):
        """
        If no model provided, create a LogisticRegression pipeline.
        """
        if model is None:
            self.model = make_pipeline(
                StandardScaler(),
                LogisticRegression(max_iter=200)
            )
            self.is_trained = False
        else:
            self.model = model
            self.is_trained = True

    def preprocess_roi(self, roi):
        """
        Convert a bubble ROI (numpy array) into a flat feature vector.
        Normalizes size → 20x20 grayscale.
        """
        if roi is None or roi.size == 0:
            return np.zeros((400,), dtype=np.float32)
        
        gray = roi if len(roi.shape) == 2 else cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (20, 20))
        normed = resized.astype(np.float32) / 255.0
        return normed.flatten()

    def train(self, roi_list, labels):
        """
        Train classifier.
        roi_list: list of numpy arrays (cropped bubble images)
        labels: list/array of 0 (empty) or 1 (filled)
        """
        X = [self.preprocess_roi(roi) for roi in roi_list]
        X = np.array(X)
        y = np.array(labels)
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, roi):
        """
        Predict 0 (empty) or 1 (filled) for a given bubble ROI.
        If not trained, fallback to simple thresholding.
        """
        if not self.is_trained:
            return self._threshold_fallback(roi)

        features = self.preprocess_roi(roi).reshape(1, -1)
        return int(self.model.predict(features)[0])

    def _threshold_fallback(self, roi):
        """
        Simple heuristic fallback if no trained model is available:
        Count black pixels ratio inside ROI.
        """
        if roi is None or roi.size == 0:
            return 0
        gray = roi if len(roi.shape) == 2 else cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        norm = cv2.resize(gray, (20, 20))
        filled_ratio = np.count_nonzero(norm < 128) / float(norm.size)
        return 1 if filled_ratio > 0.15 else 0
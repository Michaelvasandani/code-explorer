"""Tests for the question_generator module."""

import pytest
from unittest.mock import patch
from baseline.question_generator import generate_questions
from baseline.models import Question


class TestQuestionGenerator:
    """Tests for onboarding question generation."""

    @pytest.fixture
    def sample_findings(self):
        """Sample findings for question generation."""
        return [
            {
                "id": "finding_1",
                "type": "bug",
                "location": "JournalStore.swift:24",
                "confidence": "high",
                "explanation": "Force-try on JSONDecoder will crash if data is malformed"
            },
            {
                "id": "finding_2",
                "type": "architecture",
                "location": "Multiple files",
                "confidence": "medium",
                "explanation": "Inconsistent singleton usage across JournalStore and WeatherCache"
            },
            {
                "id": "finding_3",
                "type": "test_gap",
                "location": "JournalStore.swift",
                "confidence": "high",
                "explanation": "No tests for critical persistence logic"
            }
        ]

    @pytest.fixture
    def sample_summary(self):
        """Sample high-level summary."""
        return {
            "architecture_pattern": "Mixed UIKit/SwiftUI with MVVM",
            "key_components": ["JournalStore", "WeatherClient", "ViewModels"],
            "primary_risks": ["Force unwraps", "No tests"]
        }

    @pytest.fixture
    def mock_questions_response(self):
        """Mock OpenAI response for question generation."""
        return {
            "questions": [
                {
                    "question": "What is the error handling strategy for the persistence layer?",
                    "why_it_matters": "The force-try in JournalStore will crash the app if decoding fails",
                    "related_findings": ["finding_1"],
                    "areas_affected": ["Persistence", "Data loading"]
                },
                {
                    "question": "Why is the architecture mixing UIKit and SwiftUI?",
                    "why_it_matters": "Understanding the transition strategy helps avoid introducing inconsistencies",
                    "related_findings": [],
                    "areas_affected": ["UI layer", "Architecture"]
                }
            ]
        }

    def test_generate_questions_returns_list_of_questions(self, sample_findings, sample_summary, mock_questions_response):
        """Test that question generation returns a list of Question objects."""
        with patch('baseline.question_generator.call_openai') as mock_call:
            mock_call.return_value = (mock_questions_response, 0.003, 1.0, 150, 100)

            questions = generate_questions(sample_findings, sample_summary)

            assert isinstance(questions, list)
            assert all(isinstance(q, Question) for q in questions)
            assert len(questions) > 0

    def test_generate_questions_creates_actionable_questions(self, sample_findings, sample_summary, mock_questions_response):
        """Test that generated questions are actionable."""
        with patch('baseline.question_generator.call_openai') as mock_call:
            mock_call.return_value = (mock_questions_response, 0.003, 1.0, 150, 100)

            questions = generate_questions(sample_findings, sample_summary)

            for question in questions:
                assert question.question != ""
                assert question.why_it_matters != ""
                assert "?" in question.question  # Should be a question

    def test_generate_questions_links_to_findings(self, sample_findings, sample_summary, mock_questions_response):
        """Test that questions link to related findings."""
        with patch('baseline.question_generator.call_openai') as mock_call:
            mock_call.return_value = (mock_questions_response, 0.003, 1.0, 150, 100)

            questions = generate_questions(sample_findings, sample_summary)

            # At least some questions should reference findings
            questions_with_findings = [q for q in questions if q.related_findings]
            assert len(questions_with_findings) > 0

    def test_generate_questions_identifies_affected_areas(self, sample_findings, sample_summary, mock_questions_response):
        """Test that questions identify affected areas."""
        with patch('baseline.question_generator.call_openai') as mock_call:
            mock_call.return_value = (mock_questions_response, 0.003, 1.0, 150, 100)

            questions = generate_questions(sample_findings, sample_summary)

            questions_with_areas = [q for q in questions if q.areas_affected]
            assert len(questions_with_areas) > 0

    def test_generate_questions_assigns_unique_ids(self, sample_findings, sample_summary, mock_questions_response):
        """Test that each question gets a unique ID."""
        with patch('baseline.question_generator.call_openai') as mock_call:
            mock_call.return_value = (mock_questions_response, 0.003, 1.0, 150, 100)

            questions = generate_questions(sample_findings, sample_summary)

            ids = [q.id for q in questions]
            assert len(ids) == len(set(ids))  # All unique
            assert all(id.startswith("question_") for id in ids)

    def test_generate_questions_handles_empty_findings(self, sample_summary):
        """Test that question generation handles empty findings."""
        empty_response = {"questions": []}
        with patch('baseline.question_generator.call_openai') as mock_call:
            mock_call.return_value = (empty_response, 0.001, 0.5, 50, 25)

            questions = generate_questions([], sample_summary)

            assert isinstance(questions, list)
            assert len(questions) == 0

    def test_generate_questions_focuses_on_onboarding(self, sample_findings, sample_summary, mock_questions_response):
        """Test that questions are oriented toward onboarding."""
        with patch('baseline.question_generator.call_openai') as mock_call:
            mock_call.return_value = (mock_questions_response, 0.003, 1.0, 150, 100)

            questions = generate_questions(sample_findings, sample_summary)

            # Questions should help someone understand the codebase
            # They should reference architecture, patterns, or critical risks
            assert len(questions) > 0
            for question in questions:
                assert len(question.question) > 10  # Substantive questions

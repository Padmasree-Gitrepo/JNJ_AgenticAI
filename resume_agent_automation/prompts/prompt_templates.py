from __future__ import annotations


class PromptTemplates:
    @staticmethod
    def welcome_message() -> str:
        return (
            "You are assisting a user with updating their resume and profile. "
            "Ask clear, relevant questions one step at a time, do not invent missing facts, "
            "and request missing information only when necessary."
        )

    @staticmethod
    def candidate_profile() -> str:
        return (
            "Candidate context: the user is a professional employee who wants to update a resume/profile. "
            "Only include information that is explicitly provided by the user or approved in the session. "
            "Do not invent employers, dates, roles, skills, achievements, or projects."
        )

    @staticmethod
    def ask_for_missing_detail(field_name: str) -> str:
        return (
            f"The user has not provided enough information for '{field_name}'. "
            "Ask a focused clarification question to obtain the missing detail without guessing."
        )

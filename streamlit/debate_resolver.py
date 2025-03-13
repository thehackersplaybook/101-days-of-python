import streamlit as st
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import traceback
import os

load_dotenv(override=True, dotenv_path=".env")

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class Participant(BaseModel):
    name: str
    description: str
    opener: str
    opinions: list[str]


class State:
    def __init__(self):
        self.participants: list[Participant] = []
        self.debate_context = ""

    def add_participant(self, participant: Participant) -> None:
        existing_participant = self.get_participant_by_name(participant.name)
        if existing_participant:
            st.warning(f"Participant {participant.name} already exists!")
            return
        self.participants.append(participant)

    def add_participant_opinion(self, name: str, opinion: str) -> None:
        participant = self.get_participant_by_name(name)
        if participant:
            participant.opinions.append(opinion)

    def get_participant_by_name(self, name: str) -> Participant:
        return next(
            (
                participant
                for participant in self.participants
                if participant.name == name
            ),
            None,
        )

    def add_debate_context(self, context: str) -> None:
        self.debate_context = context

    def get_debate_context(self) -> str:
        return self.debate_context

    def get_participants(self) -> list[Participant]:
        return self.participants

    def update_participant(self, participant: Participant) -> None:
        existing_participant = self.get_participant_by_name(participant.name)
        if existing_participant:
            existing_participant = participant

    def update_participant_opinion(
        self, name: str, old_opinion: str, opinion: str
    ) -> None:
        participant = self.get_participant_by_name(name)
        try:
            participant.opinions.remove(old_opinion)
        except ValueError:
            print(f"Opinion {old_opinion} not found for participant {name}")
        if participant:
            participant.opinions.append(opinion)


@st.dialog("🙋🏽‍♂️ Add Participant")
def add_participant_dialog(state: State):
    participant_name = st.text_input("Participant Name")
    participant_description = st.text_input("Participant Description")
    participant_opener = st.text_area("Participant Opening Statement")
    add_participant_button = st.button("Add Participant")
    if add_participant_button:
        participant = Participant(
            name=participant_name, description=participant_description, opener=participant_opener, opinions=[]
        )
        state.add_participant(participant)
        st.rerun()


@st.dialog("🗣 Add Opinion")
def add_opinion_dialog(state: State, participant_name: str):
    opinion = st.text_area("Opinion")
    add_opinion_button = st.button("Submit", key=f"submit_opinion_{participant_name}")
    if add_opinion_button:
        state.add_participant_opinion(participant_name, opinion)
        st.rerun()


@st.dialog("🦉 Edit Opinion")
def edit_opinion_dialog(state: State, participant_name: str, opinion: str):
    old_opinion = opinion
    new_opinion = st.text_area("Opinion", value=opinion)
    submit_opinion_button = st.button(
        "Submit", key=f"submit_opinion_{participant_name}"
    )
    if submit_opinion_button:
        state.update_participant_opinion(
            name=participant_name, old_opinion=old_opinion, opinion=new_opinion
        )
        st.rerun()


@st.dialog("🦉 Edit Participant")
def edit_participant_dialog(state: State, participant_name: str, participant_description: str, participant_opener: str):
    participant = state.get_participant_by_name(participant_name)
    participant_name = st.text_input("Participant Name", value=participant.name)
    participant_description = st.text_area(
        "Participant Description", value=participant.description
    )
    participant_opener = st.text_area(
        "Participant Opening Statement", value=participant.opener
    )
    submit_participant_button = st.button(
        "Submit", key=f"submit_participant_{participant_name}"
    )
    if submit_participant_button:
        participant.name = participant_name
        participant.description = participant_description
        participant.opener = participant_opener
        state.update_participant(participant)
        st.rerun()


def generate_debate_resolution(participants: list[Participant], debate_context: str):
    try:
        participants_details = ""
        for participant in participants:
            participants_details += (
                f"Name: {participant.name} || Description: {participant.description}\n || Opening Statement: {participant.opener}\n"
            )
            for opinion in participant.opinions:
                participants_details += f"Opinion: {opinion}\n"

        system_prompt = f""""
            You are an advanced AI Debate Resolver built to act as an impartial mediator between two opposing arguments on any given topic. Your core purpose is to deliver a fair, unbiased, and evidence-based resolution by deeply analyzing both sides without any favoritism or emotional influence.
            Generate a resolution (output) for the debate in a proper markdown format. Also provide a detailed analysis of each side, fact verification report, strength & weakness breakdown, persuasion & bias score table, and a final conclusion.
                Your evaluation process should follow these stages:
                1. Argument Breakdown:
                Identify and list the core claims made by each side.
                Highlight supporting evidence or references provided (if any).
                Separate emotional appeals from factual claims.
                2. Fact Verification & Authenticity:
                Cross-verify factual claims using reliable sources (if external information is available).
                Label each claim as:
                ✅ Factually Accurate
                ❌ False/Misleading
                ⚠ Unverified/Opinion-Based
                Automatically identify and flag any logical fallacies (e.g., Ad hominem, Strawman, False Dichotomy).
                3. Argument Strength Scoring:
                Assign a dynamic score (0-100) to each side based on:

                Criteria	Weight	Description
                Factual Accuracy	40%	Verifiable facts & data used to support the argument
                Logical Structure	30%	Clarity, coherence, and flow of reasoning
                Persuasiveness	20%	How compelling the argument is (without manipulation)
                Emotional Bias	10%	Lower score if the argument relies heavily on emotions instead of facts
                4. Bias Detection:
                Automatically flag if either side is using:

                Emotional manipulation
                Fear-based rhetoric
                Misinformation
                Unfair generalizations
                5. Counter Argument Suggestions:
                If either side presents weak or incomplete arguments, suggest neutral counterarguments that could strengthen both sides fairly.

                6. Final Verdict (Optional or On Request):
                Provide one of the following outcomes:

                Clear Winner (If one argument is factually stronger)
                Balanced Conclusion (If both sides have equally strong points)
                No Resolution Possible (If both sides are purely opinion-based without supporting facts)
                Core Principles to Follow:
                Zero Personal Bias
                Fact over Emotion
                Clarity over Complexity
                Fairness over Popularity
                Transparency in Reasoning
                Output Structure (Always Follow This Format):

                Summary of Both Arguments
                Detailed Analysis of Each Side
                Fact Verification Report
                Strength & Weakness Breakdown
                Persuasion & Bias Score Table
                Final Conclusion
                Enable Real-Time Fact-Checking via external web search APIs to verify claims instantly before giving the final verdict.
            """

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"""Debate Context: {debate_context}
                    Participants: {participants_details}
                    """,
                },
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Failed to generate resolution. Error: {str(e)}")
        traceback.print_exc()
        return "Failed to generate resolution. Please try again later."


def main():
    app_state = None
    if "app_state" not in st.session_state:
        app_state = State()
        st.session_state.app_state = app_state
    else:
        app_state = st.session_state.app_state
    st.set_page_config(
        layout="wide",
        page_title="Debate Resolver By The Hackers Playbook",
        page_icon="🥁",
    )
    st.title("☀️ Resolve the damn debate for us!")
    st.markdown(
        "Let AI resolve debates for you — good for friends, family, professionals and everyone with a brain!"
    )
    st.sidebar.header("⛲️ Menu")
    st.sidebar.markdown(
        "Setup the debate by adding participants and context for the AI to understand things better."
    )
    debate_context_input = st.sidebar.text_area(label="💡 Debate Context")
    app_state.add_debate_context(debate_context_input)
    add_participant_button = st.sidebar.button(
        label="➕ Add Participant", use_container_width=True
    )
    if add_participant_button:
        add_participant_dialog(state=app_state)
    st.sidebar.markdown(
        "Once you've added everythig, click the button below to run the magic!"
    )
    run_magic_button = st.sidebar.button(label="🔮 Run Magic", use_container_width=True)

    participants = app_state.get_participants()

    st.markdown("## Participants")
    for participant in participants:
        st.write(f"**{participant.name}**: {participant.description} \n\n **Opening Statement:** {participant.opener}")
        if len(participant.opinions) > 0:
            st.markdown("### Opinions")
            opinion_count = 0
            for opinion in participant.opinions:
                st.write(f"- {opinion}")
                edit_opinion_button = st.button(
                    "Edit Opinion",
                    key=f"edit_opinion_main_{participant.name}_{str(opinion_count)}",
                )
                if edit_opinion_button:
                    edit_opinion_dialog(
                        state=app_state,
                        participant_name=participant.name,
                        opinion=opinion,
                    )
                delete_opinion = st.button(
                    "Delete Opinion", key=f"delete_opinion_main_{str(opinion_count)}"
                )
                if delete_opinion:
                    participant.opinions.remove(opinion)
                    st.rerun()
                opinion_count += 1
            st.write("---")
        cols = st.columns([1, 8])
        with cols[0]:
            edit_participant = st.button(
                f"Edit Participant", key=f"edit_participant_{participant.name}"
            )
            if edit_participant:
                edit_participant_dialog(
                    state=app_state, participant_name=participant.name, participant_description=participant.description, participant_opener=participant.opener
                )
        with cols[1]:
            add_opinion_button = st.button(
                f"Add Opinion", key=f"add_opinion_{participant.name}"
            )
            if add_opinion_button:
                add_opinion_dialog(state=app_state, participant_name=participant.name)

    if run_magic_button:
        participants = app_state.get_participants()
        debate_context_input = app_state.get_debate_context()
        if not debate_context_input:
            st.error("Please provide a debate context!")
            return
        if len(participants) < 2:
            st.error("Please add atleast 2 participants!")
            return
        spinner = st.spinner("Generating resolution...")
        resolution = generate_debate_resolution(
            participants=participants, debate_context=debate_context_input
        )
        st.markdown("## 🎉 Debate Resolution")
        st.write(resolution)
        st.success("🎉 Resolution ready!")
        st.balloons()


if __name__ == "__main__":
    main()

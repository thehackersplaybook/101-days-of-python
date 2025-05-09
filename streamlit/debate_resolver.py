import streamlit as st
from pydantic import BaseModel
from dotenv import load_dotenv
import traceback
import os
from openai import OpenAI
from openai._exceptions import OpenAIError
load_dotenv(verbose=True, override=True, dotenv_path=".env")

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class Participant(BaseModel):
    name: str
    description: str
    opener: str
    opinions: list[str]

def validate_openai_key(openai_key: str) -> bool:
    """
    Validates the OpenAI API key by making a test request using the OpenAI v1 API.
    
    Args:
        openai_key (str): The OpenAI API key to validate.
        
    Returns:
        bool: True if the key is valid, False otherwise.
    """
    if not openai_key:
        return False
    try:
        OpenAI(api_key=openai_key).models.list()
        return True
    except OpenAIError:
        return False
    except Exception as e:
        print(f"Unexpected issue during API key validation: {e}")
        traceback.print_exc()
        return False

class State:
    def __init__(self):
        """
        Initializes a State object.

        Args:
            None

        Returns:
            None
        """
        self.participants: list[Participant] = []
        self.debate_context = ""



    def add_participant(self, participant: Participant) -> None:
        """
        Adds a participant to the state.

        Args:
            participant (Participant): Participant to be added.

        Returns:
            None
        """
        existing_participant = self.get_participant_by_name(participant.name)
        if existing_participant:
            st.warning(f"Participant {participant.name} already exists!")
            return
        self.participants.append(participant)

    def add_participant_opinion(self, name: str, opinion: str) -> None:
        """
        Adds an opinion for a participant.

        Args:
            name (str): Name of the participant.
            opinion (str): Opinion to be added.

        Returns:
            None
        """
        participant = self.get_participant_by_name(name)
        if participant:
            participant.opinions.append(opinion)

    def get_participant_by_name(self, name: str) -> Participant:
        """
        Retrieves a participant by name.

        Args:
            name (str): Name of the participant.

        Returns:
            Participant: Participant with the given name.
        """
        return next(
            (
                participant
                for participant in self.participants
                if participant.name == name
            ),
            None,
        )

    def add_debate_context(self, context: str) -> None:
        """
        Adds a debate context to the state.

        Args:
            context (str): Debate context to be added.

        Returns:
            None
        """
        self.debate_context = context

    def get_debate_context(self) -> str:
        """
        Retrieves the debate context from the state.

        Args:
            None

        Returns:        
            str: Debate context.
        """
        return self.debate_context

    def get_participants(self) -> list[Participant]:
        """
        Retrieves the participants from the state.

        Args:
            None

        Returns:        
            list[Participant]: List of participants.
        """
        return self.participants

    def update_participant(self, participant: Participant) -> None:
        """
        Updates a participant in the state.

        Args:
            participant (Participant): Participant to be updated.

        Returns:
            None
        """
        existing_participant = self.get_participant_by_name(participant.name)
        if existing_participant:
            existing_participant = participant

    def update_participant_opinion(
        self, name: str, old_opinion: str, opinion: str
    ) -> None:
        """
        Updates an opinion for a participant.

        Args:
            name (str): Name of the participant.
            old_opinion (str): Old opinion to be removed.
            opinion (str): New opinion to be added.

        Returns:
            None
        """
        participant = self.get_participant_by_name(name)
        try:
            participant.opinions.remove(old_opinion)
        except ValueError:
            print(f"Opinion {old_opinion} not found for participant {name}")
        if participant:
            participant.opinions.append(opinion)


@st.dialog("🙋🏽‍♂️ Add Participant")
def add_participant_dialog(state: State)->None:
    """
    Adds a participant to the state.

    Args:
        state (State): State object to add the participant to.

    Returns:
        None
    """
    col1, col2 = st.columns(2)
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
def add_opinion_dialog(state: State, participant_name: str)->None:
    """
    Adds an opinion for a participant.

    Args:
        state (State): State object to add the opinion to.
        participant_name (str): Name of the participant.

    Returns:
        None
    """
    opinion = st.text_area("Opinion")
    add_opinion_button = st.button("Submit", key=f"submit_opinion_{participant_name}")
    if add_opinion_button:
        state.add_participant_opinion(participant_name, opinion)
        st.rerun()


@st.dialog("🦉 Edit Opinion")
def edit_opinion_dialog(state: State, participant_name: str, opinion: str):
    """
    Edits an opinion for a participant.

    Args:
        state (State): State object to edit the opinion in.
        participant_name (str): Name of the participant.
        opinion (str): Opinion to be edited.

    Returns:
        None
    """
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
    """
    Edits a participant in the state.

    Args:
        state (State): State object to edit the participant in.
        participant_name (str): Name of the participant.
        participant_description (str): Description of the participant.
        participant_opener (str): Opening statement of the participant.

    Returns:
        None
    """
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


def generate_debate_resolution(participants: list[Participant], debate_context: str, openai_key: str) -> str:
    """
    Generates a debate resolution based on the given participants and debate context.

    Args:    
        participants (list[Participant]): List of participants in the debate.
        debate_context (str): Context of the debate.

    Returns:            
        str: Debate resolution.
    """
    try:
        # Set OpenAI API key
        OpenAI.api_key = openai_key
        if not openai_key:
            raise ValueError("OpenAI API key is required.")
        
        with st.spinner("Generating resolution...", show_time=True):
            participants_details = ""
            for participant in participants:
                participants_details += (
                    f"Name: {participant.name} || Description: {participant.description}\n || Opening Statement: {participant.opener}\n"
                )
                for opinion in participant.opinions:
                    participants_details += f"Opinion: {opinion}\n"

            system_prompt = f""""
            # 🤖 System Prompt: AI Debate Resolver

            ---

            You are an **AI Debate Resolver** whose goal is to deliver a **fair, unbiased, and evidence-based resolution** between two opposing arguments.

            ---

            ### Your Tasks:
            - Provide a **resolution** in markdown format.
            - Include:
              - Detailed analysis of each side
              - Fact verification report
              - Strength & weakness breakdown
              - Persuasion & bias score table
              - Final conclusion

            ---

            ### Evaluation Steps:

            ---

            1. **Argument Breakdown**  
               - List the core claims made by each side.  
               - Highlight supporting evidence or references.  
               - Separate emotional appeals from factual claims.  

            ---

            2. **Fact Verification & Authenticity**  
               - Cross-verify factual claims using reliable sources.  
               - Tag claims as:  
                 - ✅ Factually Accurate  
                 - ❌ False / Misleading  
                 - ⚠️ Unverified / Opinion-Based  
               - Identify logical fallacies (e.g., Ad Hominem, Strawman).  

            ---

            3. **Argument Strength Scoring**  
               - Score each side based on:  
                 - Factual Accuracy (40%)  
                 - Logical Structure (30%)  
                 - Persuasiveness (20%)  
                 - Emotional Bias (10%)  

            ---

            4. **Bias Detection**  
               - Flag emotional manipulation, fear rhetoric, misinformation, and generalizations.  

            ---

            5. **Counter-Argument Suggestions**  
               - Suggest neutral counterarguments to strengthen weak points fairly.  

            ---

            6. **Final Verdict (Optional)**  
               - Provide one outcome:  
                 - Clear Winner  
                 - Balanced Conclusion  
                 - No Resolution Possible  

            ---

            ### Principles to Follow:

            ---

            - Zero Personal Bias  
            - Facts Over Emotion  
            - Clarity Over Complexity  
            - Fairness Over Popularity  
            - Transparency in Reasoning  

            ---

            ### Output Structure:

            ---

            1. Summary of Both Arguments  
            2. Detailed Analysis of Each Side  
            3. Fact Verification Report  
            4. Strength & Weakness Breakdown  
            5. Persuasion & Bias Score Table  
            6. Final Conclusion  
        
        Also just above the final conclusion, provide the debate winners name in bold and in big size and on separate line and then the final conclusion.
            ---
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
        
    st.set_page_config(layout="wide", page_title="Debate Resolver By The Hackers Playbook", page_icon="🥁")
    st.title("☀️ Resolve the damn debate for us!")
    st.markdown(
        "Let AI resolve debates for you — good for friends, family, professionals and everyone with a brain!"
    )
    
    st.sidebar.header("🔑 API Key Management")
    openai_key = st.sidebar.text_input("Enter your OpenAI API Key:", type="password", key="api_key_input_sidebar", placeholder="sk-XXXXXXXXXXXXXXXXXXXXXXXXXX", help="Get your API key from https://platform.openai.com/signup")

    col1, col2 = st.sidebar.columns(2)

    with st.sidebar:
        if col1.button("💾 Save API Key"):
            if not openai_key:
                st.warning("❌ Please fill in the API key field before saving.")
            else:
                with st.spinner("⏳ Validating API key..."):
                    is_valid = validate_openai_key(openai_key)
                    if is_valid:
                        st.toast("API key saved successfully! ✅")
                    else:
                        st.toast("Invalid OpenAI API key. Please check and try again. ❌")

        if col2.button("🔄 Reset API Key"):
            if not openai_key :
                st.warning("❌ No API key to reset.")
            else:
                with st.spinner("Resetting API key..."):
                    st.session_state.openai_key = None
                    st.success("OpenAI API key reset successfully!")
        st.markdown("---")


    st.sidebar.header("⚙️ Debate Configuration")
    st.sidebar.markdown(
        "Setup the debate by adding participants and context for the AI to understand things better."
    )
    debate_context_input = st.sidebar.text_area(label="💡 Debate Context", placeholder = "e.g., Should AI be regulated by governments?")
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
    # Create three columns for participants
    if participants:
        # Distribute participants across the three columns
        cols = st.columns([1,1],gap="small")
        for i, participant in enumerate(participants):
            with cols[i % 3]:  # Alternate between the three columns
                with st.expander(f"👥 Participant : {participant.name}", expanded=True):
                    st.markdown(f"### 🧠 {participant.name}")
                    st.caption(f"_{participant.description}_")
                    st.markdown(f"**Opener:** {participant.opener}")

                    # Display opinions directly (no nested expander)
                    st.markdown("#### 💬 Opinions")
                    if len(participant.opinions) > 0:
                        for opinion_count, opinion in enumerate(participant.opinions):
                            st.write(f"- {opinion}")
                            # Buttons for editing and deleting opinions directly below the opinion
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                edit_opinion_button = st.button(
                                    "✏️ Edit Opinion",
                                    key=f"edit_opinion_main_{participant.name}_{str(opinion_count)}",
                                )
                                if edit_opinion_button:
                                    edit_opinion_dialog(
                                        state=app_state,
                                        participant_name=participant.name,
                                        opinion=opinion,
                                    )
                            with col2:
                                delete_opinion = st.button(
                                    "🗑️ Delete Opinion",
                                    key=f"delete_opinion_main_{participant.name}_{str(opinion_count)}",
                                )
                                if delete_opinion:
                                    participant.opinions.remove(opinion)
                                    st.rerun()
                            st.markdown("---")
                    else:
                        st.info("No opinions added yet.")
                    
                    col1, col2 = st.columns([1, 1])
                    # Buttons for editing and adding participants
                    with col1:
                        add_opinion_button = st.button(
                            f"➕ Add Opinion", key=f"add_opinion_{participant.name}"
                        )
                        if add_opinion_button:
                            add_opinion_dialog(state=app_state, participant_name=participant.name)
                    with col2:
                        edit_participant = st.button(
                            f"✏️ Edit Participant", key=f"edit_participant_{participant.name}"
                        )
                        if edit_participant:
                            edit_participant_dialog(
                                state=app_state,
                                participant_name=participant.name,
                                participant_description=participant.description,
                                participant_opener=participant.opener,
                            )
                
    else:
        st.info("No participants added yet. Click the button in the sidebar to add one!")

    if run_magic_button:
        if not openai_key:
            st.sidebar.error("Please enter a valid OpenAI API key.")
            return 
        else:
            participants = app_state.get_participants()
            debate_context_input = app_state.get_debate_context()
            if not debate_context_input:
                st.sidebar.error("Please provide a debate context!")
                return
            if len(participants) < 2:
                st.sidebar.error("Please add atleast 2 participants!")
                return
            spinner = st.spinner("Generating resolution...")
            resolution = generate_debate_resolution(
                participants=participants, debate_context=debate_context_input, openai_key=openai_key
            )
            st.markdown(resolution)
            st.toast("🎉 Resolution ready!")
if __name__ == "__main__":
    main()

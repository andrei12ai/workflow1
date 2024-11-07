import json
import streamlit as st
from graphviz import Digraph

# Streamlit UI
st.title("DSL Workflow Analyzer and Visualizer")

st.write("""
Upload a DSL JSON file to analyze and visualize the workflow defined in it.
""")

uploaded_file = st.file_uploader("Choose a DSL JSON file", type="json")

if uploaded_file is not None:
    # Read and parse the uploaded JSON file
    dsl_data = json.load(uploaded_file)

    # Create a mapping of step IDs to step names
    step_id_to_name = {step['Id']: step['Name'] for step in dsl_data['Steps']}

    st.subheader("Workflow Details")
    st.write(f"**Workflow ID:** {dsl_data['Id']}")
    st.write(f"**Version:** {dsl_data['Version']}")
    st.write(f"**Release Version:** {dsl_data['ReleaseVersion']}")
    st.write(f"**Data Type:** {dsl_data['DataType']}")

    st.subheader("Steps Analysis")

    for step in dsl_data['Steps']:
        step_id = step.get("Id")
        step_name = step.get("Name")
        step_type = step.get("StepType")
        next_step_id = step.get("NextStepId", "None")
        next_step_name = step_id_to_name.get(next_step_id, "None") if next_step_id != "None" else "None"
        inputs = step.get("Inputs", {})
        outputs = step.get("Outputs", {})
        select_next_step = step.get("SelectNextStep", {})

        #st.write(f"**Step ID:** {step_id}")
        st.write(f"**Step Name:** {step_name}")
        #st.write(f"**Type:** {step_type}")
        st.write(f"**Next Step:** {next_step_name} ({next_step_id})")
        st.write("**Inputs**")
        st.json(inputs, expanded=False)
        st.write("**Outputs**")
        st.json(outputs, expanded=False)

        if select_next_step:
            st.write("**Conditional Transitions:**")
            for condition, condition_expr in select_next_step.items():
                condition_name = step_id_to_name.get(condition, "Unknown")
                st.write(f" - Next Step: {condition_name} ({condition}), Condition: {condition_expr}")

    # Visualization
    st.subheader("Workflow Visualization")

    def visualize_dsl(data):
        dot = Digraph(comment='DSL Workflow Visualization')

        # Add nodes for each step
        for step in data['Steps']:
            step_id = step.get("Id")
            step_name = step.get("Name")
            dot.node(step_id, f"{step_name}\n({step_id})")

        # Add edges for each step connection
        for step in data['Steps']:
            step_id = step.get("Id")
            next_step_id = step.get("NextStepId", None)
            select_next_step = step.get("SelectNextStep", {})

            # Direct next step connection
            if next_step_id:
                next_step_name = step_id_to_name.get(next_step_id, "None")
                dot.edge(step_id, next_step_id, label=f"Next: {next_step_name}")

            # Conditional connections
            for condition, condition_expr in select_next_step.items():
                condition_name = step_id_to_name.get(condition, "Unknown")
                dot.edge(step_id, condition, label=f"Condition: {condition_expr}\nNext: {condition_name}")

        return dot

    # Render the graph to a file and display in Streamlit
    graph = visualize_dsl(dsl_data)
    st.graphviz_chart(graph.source)

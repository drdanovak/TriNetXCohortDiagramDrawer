import streamlit as st
import json
from graphviz import Digraph
import tempfile

# ---- Initialize session state ----
if "diagram_data" not in st.session_state:
    st.session_state.diagram_data = {
        "title": "TriNetX Study",
        "sections": [
            {"id": "top", "label": "Top Box (e.g., Database, Date, n)", "content": "TriNetX\nUS Collaborative Network\nSeptember 2024\n(n=117,058,583)"},
            {"id": "criteria", "label": "Inclusion/Exclusion Criteria", "content": "Age >45\nExclusions: AD Comorbidities..."},
            {"id": "control", "label": "Control Group", "content": "Total: n=3,767,962\nAfter PSM: n=1,362,224"},
            {"id": "statin", "label": "Statin Group", "content": "Total: n=2,562,828\nAfter PSM: n=1,362,224"},
            {"id": "outcomes", "label": "Outcomes", "content": "No Statin AD Outcome: 5980 (44%)\nStatin AD Outcome: 1805 (13%)\nRisk Diff: -31%"},
        ],
        "edges": [
            ["top", "criteria"], ["criteria", "control"], ["criteria", "statin"], ["control", "outcomes"], ["statin", "outcomes"]
        ]
    }

# ---- Sidebar: Save/Load ----
st.sidebar.header("💾 Save/Load Diagram")
if st.sidebar.button("Download Diagram Data"):
    st.sidebar.download_button(
        label="Download JSON",
        data=json.dumps(st.session_state.diagram_data, indent=2),
        file_name="cohort_diagram.json",
        mime="application/json"
    )

uploaded = st.sidebar.file_uploader("Upload JSON to Load Diagram", type=["json"])
if uploaded is not None:
    st.session_state.diagram_data = json.load(uploaded)

# ---- Main UI: Edit Diagram ----
st.title("🧬 Cohort Diagram Builder (TriNetX Style)")

# Edit the title
st.session_state.diagram_data["title"] = st.text_input("Diagram Title", st.session_state.diagram_data["title"])

# Edit sections
st.header("Edit Diagram Sections")
for section in st.session_state.diagram_data["sections"]:
    section["content"] = st.text_area(section["label"], section["content"], height=100)

# Add/remove section capability
if st.button("Add Section"):
    st.session_state.diagram_data["sections"].append({"id": f"custom{len(st.session_state.diagram_data['sections'])}", "label": "Custom Section", "content": ""})

remove_section = st.selectbox("Remove Section", options=[s["label"] for s in st.session_state.diagram_data["sections"]])
if st.button("Remove Selected Section"):
    st.session_state.diagram_data["sections"] = [s for s in st.session_state.diagram_data["sections"] if s["label"] != remove_section]

# Edit edges (connections between boxes)
st.header("Edit Connections")
edges_str = "\n".join([f"{e[0]} -> {e[1]}" for e in st.session_state.diagram_data["edges"]])
edges_str = st.text_area("Box Connections (One per line, format: boxid -> boxid)", edges_str, height=80)
st.session_state.diagram_data["edges"] = [line.strip().split("->") for line in edges_str.split("\n") if "->" in line]

# ---- Generate Diagram with Graphviz ----
dot = Digraph(comment=st.session_state.diagram_data["title"])
for s in st.session_state.diagram_data["sections"]:
    dot.node(s["id"], s["content"], shape="box", style="filled", fillcolor="white", fontsize="12", fontname="Arial")

for e in st.session_state.diagram_data["edges"]:
    if len(e) == 2:
        dot.edge(e[0].strip(), e[1].strip())

st.subheader("Preview: Cohort Diagram")
st.graphviz_chart(dot)

# ---- Export as PNG (Optional Advanced Feature) ----
# Export PNG: Graphviz can save to file, then reload and serve as image.
if st.button("Export Diagram as PNG"):
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        dot.render(tmpfile.name, format="png")
        st.image(tmpfile.name + ".png")


import streamlit as st
from streamlit_drawable_canvas import st_canvas
import pandas as pd
import json
import uuid

# Helper: Generate unique ID for each box
def get_new_id():
    return str(uuid.uuid4())[:8]

st.title("Hybrid Cohort Diagram Builder")

# ---- Sidebar/Table for Editing Boxes ----
st.sidebar.header("📝 Edit Boxes")
if "boxes" not in st.session_state:
    # Example starting boxes: customize these as needed
    st.session_state.boxes = [
        {"id": get_new_id(), "label": "Dataset", "content": "TriNetX\nUS Collaborative Network\n(n=117,058,583)", "x": 100, "y": 60, "w": 260, "h": 90, "color": "#e3e6fa"},
        {"id": get_new_id(), "label": "Criteria", "content": "Age >45\nExclude AD Comorbidities", "x": 100, "y": 200, "w": 260, "h": 80, "color": "#fbeee6"},
        {"id": get_new_id(), "label": "Control Group", "content": "Control Group\nn=1,362,224", "x": 40, "y": 340, "w": 200, "h": 80, "color": "#d6f5e3"},
        {"id": get_new_id(), "label": "Statin Group", "content": "Statin Group\nn=1,362,224", "x": 260, "y": 340, "w": 200, "h": 80, "color": "#ffe5e5"},
        {"id": get_new_id(), "label": "Outcomes", "content": "No Statin: 44%\nStatin: 13%\nRisk Diff: -31%", "x": 150, "y": 500, "w": 260, "h": 80, "color": "#fffac8"}
    ]

# Convert boxes to dataframe for easy editing
boxes_df = pd.DataFrame(st.session_state.boxes)
edited_df = st.data_editor(
    boxes_df[["label", "content", "color"]],
    use_container_width=True,
    column_config={"color": st.column_config.ColorColumn("Box Color")},
    hide_index=True,
    num_rows="dynamic"
)
# Sync edits back to state
for i, row in edited_df.iterrows():
    st.session_state.boxes[i]["label"] = row["label"]
    st.session_state.boxes[i]["content"] = row["content"]
    st.session_state.boxes[i]["color"] = row["color"]

# ---- Canvas ----
st.header("Canvas: Drag, Move, Resize Boxes")
canvas_boxes = [
    {
        "type": "rect",
        "left": box["x"],
        "top": box["y"],
        "width": box["w"],
        "height": box["h"],
        "stroke": "#444",
        "fill": box["color"],
        "strokeWidth": 2,
        "name": box["label"],
        "text": box["content"],
        "id": box["id"],
    }
    for box in st.session_state.boxes
]

canvas_result = st_canvas(
    fill_color="#eeeeee",
    stroke_width=2,
    stroke_color="#333333",
    background_color="#fafafc",
    width=600,
    height=700,
    initial_drawing={"objects": canvas_boxes, "version": "4.4.0"},
    drawing_mode="transform",  # Drag, move, resize
    key="canvas"
)

# Update positions/sizes if moved on canvas
if canvas_result.json_data and "objects" in canvas_result.json_data:
    for obj in canvas_result.json_data["objects"]:
        for box in st.session_state.boxes:
            if "id" in obj and obj["id"] == box["id"]:
                box["x"] = obj["left"]
                box["y"] = obj["top"]
                box["w"] = obj["width"]
                box["h"] = obj["height"]

# ---- Save/Load Diagram ----
st.sidebar.header("💾 Save/Load Diagram")
if st.sidebar.button("Save as JSON"):
    st.sidebar.download_button(
        "Download Diagram JSON",
        data=json.dumps(st.session_state.boxes, indent=2),
        file_name="diagram_boxes.json"
    )

uploaded = st.sidebar.file_uploader("Load Diagram JSON", type=["json"])
if uploaded:
    boxes = json.load(uploaded)
    st.session_state.boxes = boxes

st.caption("Tip: Use the sidebar table to edit box text/colors. Drag boxes on the canvas to arrange your diagram. Save/load with JSON as needed.")

# (Optional: Add lines/arrows and richer box editing on request!)


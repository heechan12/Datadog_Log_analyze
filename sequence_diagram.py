import pandas as pd


def generate_plantuml_sequence(df, call_id):
    call_flow_df = df[(df['context.callID'] == call_id) & (
        df['Resource Url'].str.contains('res/SDK_restReq|res/SDK_longRes', case=False, na=False))].sort_values(
        by='timestamp')
    if call_flow_df.empty:
        return "@startuml\nnote right of UE : 선택된 Call ID에 유효한 메시지 없음\n@enduml"

    # Initialize PlantUML diagram
    plantuml_code = ["@startuml", "participant UE", "participant Server"]

    # Iterate through messages
    for _, row in call_flow_df.iterrows():
        timestamp = row['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(row['timestamp']) else 'Unknown Time'
        method = row['context.method']
        url = row['Resource Url']
        direction = "UE -> Server" if 'res/SDK_restReq' in url else "UE <- Server" if 'res/SDK_longRes' in url else None

        if direction == "UE -> Server":
            plantuml_code.append(f"UE -> Server: {method} [{timestamp}]")
        elif direction == "UE <- Server":
            plantuml_code.append(f"UE <- Server: {method} [{timestamp}]")

    plantuml_code.append("@enduml")
    return "\n".join(plantuml_code)


def render_plantuml(plantuml_code):
    # Return the PlantUML content directly
    return plantuml_code

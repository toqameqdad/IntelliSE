
from schemas import ActivityDiagramResult

data = {
    "diagramType": "activity",
    "systemName": "E-Commerce Order Management System",
    "activityName": "Order Placement and Payment Workflow",
    
	"nodes": [
		{
			"id": "node_1",
			"name": "Start",
			"description": "Start",
			"nodeType": "initial",
			"partition": None
		},
		{
			"id": "node_2",
			"name": "Fork",
			"description": "Fork",
			"nodeType": "fork",
			"partition": "System"
		},
		{
			"id": "node_3",
			"name": "Task A",
			"description": "First parallel task",
			"nodeType": "action",
			"partition": "System"
		},
		{
			"id": "node_4",
			"name": "Task B",
			"description": "Second parallel task",
			"nodeType": "action",
			"partition": "System"
		},
		{
			"id": "node_5",
			"name": "Join",
			"description": "Join",
			"nodeType": "join",
			"partition": "System"
		},
		{
			"id": "node_6",
			"name": "End",
			"description": "End",
			"nodeType": "activity_final",
			"partition": None
		}
	],

    
	"flows": [
		{
			"source": "node_1",
			"target": "node_2",
			"condition": None
		},
		{
			"source": "node_2",
			"target": "node_3",
			"condition": None
		},
		{
			"source": "node_2",
			"target": "node_4",
			"condition": None
		},
		{
			"source": "node_3",
			"target": "node_5",
			"condition": None
		},
		{
			"source": "node_4",
			"target": "node_5",
			"condition": None
		},
		{
			"source": "node_5",
			"target": "node_6",
			"condition": None
		},
		{
			"source": "node_3",
			"target": "node_6",
			"condition": None
		}
	]
}

try:
    result = ActivityDiagramResult.model_validate(data)
    print("Validation successful!")

except Exception as e:
    print("Validation failed:")
    print(e)


from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
        str_strip_whitespace=True,
    )


class ProjectInput(BaseSchema):
    project_name: str = Field(min_length=1)
    project_description: str = Field(min_length=20)


class Requirement(BaseSchema):
    type: Literal["functional", "non_functional"]
    description: str = Field(min_length=1)
    priority: Literal["must", "should"]
    rationale: str = Field(min_length=1)
    source: Literal["explicit", "inferred"]


class RequirementsResult(BaseSchema):
    functional_requirements: list[Requirement]
    non_functional_requirements: list[Requirement]

    @model_validator(mode="after")
    def validate_requirements(self):
        for requirement in self.functional_requirements:
            if requirement.type != "functional":
                raise ValueError(
                    "Functional requirements must have type 'functional'"
                )

        for requirement in self.non_functional_requirements:
            if requirement.type != "non_functional":
                raise ValueError(
                    "Non-functional requirements must have type 'non_functional'"
                )

        descriptions = [
            " ".join(item.description.casefold().split())
            for item in (
                self.functional_requirements
                + self.non_functional_requirements
            )
        ]

        if len(descriptions) != len(set(descriptions)):
            raise ValueError("Duplicate requirements detected")

        return self


class ClarificationQuestion(BaseSchema):
    question: str
    reason: str
    related_area: Literal[
        "functionality",
        "users",
        "business_rules",
        "data",
        "platform",
        "security",
        "performance",
        "constraints",
    ]


class ClarificationResult(BaseSchema):
    needs_clarification: bool
    questions: list[ClarificationQuestion]


class ClarificationAnswer(BaseSchema):
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)


class ClarificationAnswersInput(ProjectInput):
    answers: list[ClarificationAnswer] = Field(min_length=1)


class RequirementsGenerationInput(ProjectInput):
    answers: list[ClarificationAnswer] = Field(default_factory=list)



class SRSInput(BaseSchema):
    project_name: str = Field(min_length=1)
    project_description: str = Field(min_length=20)
    functional_requirements: list[Requirement] = Field(min_length=1)
    non_functional_requirements: list[Requirement] = Field(min_length=1)


class SRSIntroduction(BaseSchema):
    purpose: str
    scope: str
    definitions_and_acronyms: list[str]


class SRSOverallDescription(BaseSchema):
    product_perspective: str
    user_classes: list[str]
    operating_environment: str
    design_and_implementation_constraints: list[str]
    assumptions_and_dependencies: list[str]


class SRSWorkflow(BaseSchema):
    main_workflow: list[str]
    stage_approval_and_dependency_rules: list[str]
    project_status: list[str]


class SRSRequirement(BaseSchema):
    id: str
    description: str


class SRSNonFunctionalRequirement(BaseSchema):
    id: str
    category: str
    description: str


class SRSDataRequirements(BaseSchema):
    main_data_entities: list[str]
    data_ownership_and_deletion: str


class SRSExternalInterfaces(BaseSchema):
    user_interface: list[str]
    ai_service_interface: str
    email_interface: str
    export_interface: str


class SRSResult(BaseSchema):
    introduction: SRSIntroduction
    overall_description: SRSOverallDescription
    system_workflow_and_state_rules: SRSWorkflow
    functional_requirements: list[SRSRequirement]
    non_functional_requirements: list[SRSNonFunctionalRequirement]
    data_requirements: SRSDataRequirements
    business_rules: list[str]
    external_interface_requirements: SRSExternalInterfaces
    acceptance_criteria: list[str]
    implementation_decisions: list[str]



class ContextDiagramSystem(BaseSchema):
    id: Literal["system"] = "system"
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)


class ContextExternalEntity(BaseSchema):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)


class ContextDataFlow(BaseSchema):
    id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    target: str = Field(min_length=1)
    label: str = Field(min_length=1)


class ContextDiagramResult(BaseSchema):
    diagram_type: Literal["context"] = "context"
    system: ContextDiagramSystem
    external_entities: list[ContextExternalEntity]
    data_flows: list[ContextDataFlow]
    warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_diagram(self):
        entity_ids = [entity.id for entity in self.external_entities]

        if "system" in entity_ids:
            raise ValueError(
                "External entity IDs cannot use the reserved ID 'system'"
            )

        if len(entity_ids) != len(set(entity_ids)):
            raise ValueError("Duplicate external entity IDs detected")

        flow_ids = [flow.id for flow in self.data_flows]

        if len(flow_ids) != len(set(flow_ids)):
            raise ValueError("Duplicate data flow IDs detected")

        valid_ids = {"system", *entity_ids}

        for flow in self.data_flows:
            if flow.source not in valid_ids:
                raise ValueError(
                    f"Unknown source ID: {flow.source}"
                )

            if flow.target not in valid_ids:
                raise ValueError(
                    f"Unknown target ID: {flow.target}"
                )

            if flow.source == flow.target:
                raise ValueError(
                    "A data flow cannot connect an element to itself"
                )

            if "system" not in (flow.source, flow.target):
                raise ValueError(
                    "Every context data flow must connect to the system"
                )

        return self



class UseCaseDiagramActor(BaseSchema):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    actor_type: Literal["human", "external_system"]


class UseCaseDiagramItem(BaseSchema):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    actor_ids: list[str] = Field(default_factory=list)


class UseCaseRelationship(BaseSchema):
    source: str = Field(min_length=1)
    target: str = Field(min_length=1)
    relationship_type: Literal["include", "extend"]


class UseCaseDiagramResult(BaseSchema):
    diagram_type: Literal["use_case"] = "use_case"
    system_name: str = Field(min_length=1)
    actors: list[UseCaseDiagramActor] = Field(min_length=1)
    use_cases: list[UseCaseDiagramItem] = Field(min_length=1)
    relationships: list[UseCaseRelationship] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_diagram(self):
        actor_ids = [actor.id for actor in self.actors]
        use_case_ids = [use_case.id for use_case in self.use_cases]

        if len(actor_ids) != len(set(actor_ids)):
            raise ValueError("Actor IDs must be unique")

        if len(use_case_ids) != len(set(use_case_ids)):
            raise ValueError("Use case IDs must be unique")

        valid_actor_ids = set(actor_ids)
        valid_use_case_ids = set(use_case_ids)

        for use_case in self.use_cases:
            if not set(use_case.actor_ids).issubset(valid_actor_ids):
                raise ValueError(
                    f"Use case '{use_case.id}' references an unknown actor"
                )

        for relationship in self.relationships:
            if (
                relationship.source not in valid_use_case_ids
                or relationship.target not in valid_use_case_ids
            ):
                raise ValueError(
                    "Relationship references an unknown use case"
                )

            if relationship.source == relationship.target:
                raise ValueError(
                    "A use case cannot have a relationship with itself"
                )

        return self



class ActivityDiagramNode(BaseSchema):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    node_type: Literal[
        "initial",
        "action",
        "decision",
        "merge",
        "fork",
        "join",
        "activity_final",
    ]
    partition: str | None = None


class ActivityDiagramFlow(BaseSchema):
    source: str = Field(min_length=1)
    target: str = Field(min_length=1)
    condition: str | None = None


class ActivityDiagramResult(BaseSchema):
    diagram_type: Literal["activity"] = "activity"
    system_name: str = Field(min_length=1)
    activity_name: str = Field(min_length=1)
    nodes: list[ActivityDiagramNode] = Field(min_length=2)
    flows: list[ActivityDiagramFlow] = Field(min_length=1)

    
    @model_validator(mode="after")
    def validate_diagram(self):
        node_ids = [node.id for node in self.nodes]

        if len(node_ids) != len(set(node_ids)):
            raise ValueError("Node IDs must be unique")

        valid_node_ids = set(node_ids)

        for flow in self.flows:
            if (
                flow.source not in valid_node_ids
                or flow.target not in valid_node_ids
            ):
                raise ValueError("Flow references an unknown node")

            if flow.source == flow.target:
                raise ValueError("A node cannot have a flow to itself")

        initial_nodes = [
            node for node in self.nodes
            if node.node_type == "initial"
        ]

        final_nodes = [
            node for node in self.nodes
            if node.node_type == "activity_final"
        ]

        if len(initial_nodes) != 1:
            raise ValueError(
                "Activity diagram must have exactly one initial node"
            )

        if not final_nodes:
            raise ValueError(
                "Activity diagram must have at least one final node"
            )

        for node in self.nodes:
            if node.node_type == "decision":
                outgoing_flows = [
                    flow for flow in self.flows
                    if flow.source == node.id
                ]

                if len(outgoing_flows) < 2:
                    raise ValueError(
                        f"Decision node '{node.id}' must have "
                        "at least two outgoing flows"
                    )

                if any(
                    not flow.condition
                    for flow in outgoing_flows
                ):
                    raise ValueError(
                        f"All outgoing flows from decision "
                        f"'{node.id}' must have conditions"
                    )

        # Validate Fork and Join nodes
        for node in self.nodes:

            incoming_flows = [
                flow for flow in self.flows
                if flow.target == node.id
            ]

            outgoing_flows = [
                flow for flow in self.flows
                if flow.source == node.id
            ]

            if node.node_type == "fork":

                if len(incoming_flows) != 1:
                    raise ValueError(
                        f"Fork node '{node.id}' must have "
                        "exactly one incoming flow"
                    )

                if len(outgoing_flows) < 2:
                    raise ValueError(
                        f"Fork node '{node.id}' must have "
                        "at least two outgoing flows"
                    )

            if node.node_type == "join":

                if len(incoming_flows) < 2:
                    raise ValueError(
                        f"Join node '{node.id}' must have "
                        "at least two incoming flows"
                    )

                if len(outgoing_flows) != 1:
                    raise ValueError(
                        f"Join node '{node.id}' must have "
                        "exactly one outgoing flow"
                    )

        # Validate Fork and Join relationships
        adjacency = {node.id: [] for node in self.nodes}

        for flow in self.flows:
            adjacency[flow.source].append(flow.target)

        join_ids = {
            node.id for node in self.nodes
            if node.node_type == "join"
        }

        def get_reachable_nodes(start_id: str) -> set[str]:
            visited = set()
            stack = [start_id]

            while stack:
                current = stack.pop()

                if current in visited:
                    continue

                visited.add(current)
                stack.extend(adjacency[current])

            return visited

        for node in self.nodes:
            if node.node_type != "fork":
                continue

            outgoing_flows = [
                flow for flow in self.flows
                if flow.source == node.id
            ]

            branch_targets = {
                flow.target for flow in outgoing_flows
            }

            if len(branch_targets) != len(outgoing_flows):
                raise ValueError(
                    f"Fork node '{node.id}' must have "
                    "different targets for each branch"
                )

            reachable_sets = [
                get_reachable_nodes(target)
                for target in branch_targets
            ]

            common_reachable_nodes = set.intersection(
                *reachable_sets
            )

            matching_joins = (
                common_reachable_nodes & join_ids
            )

            
            valid_joins = set()

            for join_id in matching_joins:
                all_branches_pass_through_join = True

                for branch_target in branch_targets:
                    visited = set()
                    stack = [branch_target]

                    while stack:
                        current = stack.pop()

                        if current == join_id or current in visited:
                            continue

                        visited.add(current)
                        stack.extend(adjacency[current])

                    if any(
                        final.id in visited
                        for final in final_nodes
                    ):
                        all_branches_pass_through_join = False
                        break

                if all_branches_pass_through_join:
                    valid_joins.add(join_id)

            if not valid_joins:
                raise ValueError(
                    f"Fork node '{node.id}' has branches "
                    "that can reach an activity final "
                    "without passing through a common join"
                )


        # Check that every node is reachable from the initial node.
        adjacency = {
            node.id: [] for node in self.nodes
        }

        for flow in self.flows:
            adjacency[flow.source].append(flow.target)

        visited = set()
        stack = [initial_nodes[0].id]

        while stack:
            current_node = stack.pop()

            if current_node in visited:
                continue

            visited.add(current_node)
            stack.extend(adjacency[current_node])

        unreachable_nodes = valid_node_ids - visited

        if unreachable_nodes:
            raise ValueError(
                f"Unreachable nodes found: {sorted(unreachable_nodes)}"
            )


        # Check that every node can reach at least one final node.
        reverse_adjacency = {
            node.id: [] for node in self.nodes
        }

        for flow in self.flows:
            reverse_adjacency[flow.target].append(flow.source)

        nodes_reaching_final = set()
        stack = [node.id for node in final_nodes]

        while stack:
            current_node = stack.pop()

            if current_node in nodes_reaching_final:
                continue

            nodes_reaching_final.add(current_node)

            stack.extend(
                reverse_adjacency[current_node]
            )

        nodes_without_final_path = (
            valid_node_ids - nodes_reaching_final
        )

        if nodes_without_final_path:
            raise ValueError(
                "Nodes cannot reach an activity final: "
                f"{sorted(nodes_without_final_path)}"
            )


        # Check that every node can reach at least one activity final.
        reverse_adjacency = {
            node.id: [] for node in self.nodes
        }

        for flow in self.flows:
            reverse_adjacency[flow.target].append(flow.source)

        can_reach_final = set()
        stack = [node.id for node in final_nodes]

        while stack:
            current_node = stack.pop()

            if current_node in can_reach_final:
                continue

            can_reach_final.add(current_node)

            stack.extend(
                reverse_adjacency[current_node]
            )

        nodes_without_final_path = (
            valid_node_ids - can_reach_final
        )

        if nodes_without_final_path:
            raise ValueError(
                "Nodes cannot reach an activity final: "
                f"{sorted(nodes_without_final_path)}"
            )


        return self



class ObjectDiagramAttribute(BaseSchema):
    name: str = Field(min_length=1)
    value: str = Field(min_length=1)


class ObjectDiagramObject(BaseSchema):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    class_name: str = Field(min_length=1)
    attributes: list[ObjectDiagramAttribute] = Field(
        default_factory=list
    )

    @model_validator(mode="after")
    def validate_attributes(self):
        attribute_names = [
            attribute.name.casefold()
            for attribute in self.attributes
        ]

        if len(attribute_names) != len(set(attribute_names)):
            raise ValueError(
                f"Object '{self.id}' has duplicate attributes"
            )

        return self


class ObjectDiagramLink(BaseSchema):
    source: str = Field(min_length=1)
    target: str = Field(min_length=1)
    label: str = Field(min_length=1)


class ObjectDiagramResult(BaseSchema):
    diagram_type: Literal["object"] = "object"
    system_name: str = Field(min_length=1)
    objects: list[ObjectDiagramObject] = Field(min_length=1)
    links: list[ObjectDiagramLink] = Field(
        default_factory=list
    )

    @model_validator(mode="after")
    def validate_diagram(self):
        object_ids = [obj.id for obj in self.objects]

        if len(object_ids) != len(set(object_ids)):
            raise ValueError("Object IDs must be unique")

        valid_ids = set(object_ids)

        for link in self.links:
            if (
                link.source not in valid_ids
                or link.target not in valid_ids
            ):
                raise ValueError(
                    "Link references an unknown object"
                )

        return self

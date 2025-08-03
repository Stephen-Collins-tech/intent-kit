import uuid
from typing import List, Optional
from abc import ABC, abstractmethod
from intent_kit.utils.logger import Logger
from intent_kit.context import IntentContext
from intent_kit.nodes.types import ExecutionResult
from intent_kit.nodes.enums import NodeType


class Node:
    """Base class for all nodes with UUID identification and optional user-defined names."""

    def __init__(self, name: Optional[str] = None, parent: Optional["Node"] = None):
        self.node_id = str(uuid.uuid4())
        self.name = name or self.node_id
        self.parent = parent

    @property
    def has_name(self) -> bool:
        return self.name is not None

    def get_path(self) -> List[str]:
        path = []
        node: Optional["Node"] = self
        while node:
            path.append(node.name)
            node = node.parent
        return list(reversed(path))

    def get_path_string(self) -> str:
        return ".".join(self.get_path())

    def get_uuid_path(self) -> List[str]:
        path = []
        node: Optional["Node"] = self
        while node:
            path.append(node.node_id)
            node = node.parent
        return list(reversed(path))

    def get_uuid_path_string(self) -> str:
        return ".".join(self.get_uuid_path())


class TreeNode(Node, ABC):
    """Base class for all nodes in the intent tree."""

    logger: Logger

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        description: str,
        children: Optional[List["TreeNode"]] = None,
        parent: Optional["TreeNode"] = None,
    ):
        super().__init__(name=name, parent=parent)
        self.logger = Logger(name or self.__class__.__name__.lower())
        self.description = description
        self.children: List["TreeNode"] = list(children) if children else []
        for child in self.children:
            child.parent = self

    @property
    def node_type(self) -> NodeType:
        """Get the type of this node. Override in subclasses."""
        return NodeType.UNKNOWN

    @abstractmethod
    def execute(
        self, user_input: str, context: Optional[IntentContext] = None
    ) -> ExecutionResult:
        """Execute the node with the given user input and optional context."""
        pass

    def traverse(self, user_input, context=None, parent_path=None):
        """
        Traverse the node and its children, executing each node and aggregating results.
        Iterative implementation (no recursion).
        Returns the final (deepest) child result, or the root result if no children are traversed.
        Aggregates input_tokens and output_tokens from all traversed nodes.
        """
        parent_path = parent_path or []
        stack: List[tuple[TreeNode, List[str], ExecutionResult, int]] = []
        # Each stack entry: (node, parent_path, parent_result, child_idx)
        # parent_result is None for the root node

        # Execute root node
        root_result = self.execute(user_input, context)

        root_result.node_name = self.name
        root_result.node_path = parent_path + [self.name]
        if root_result.error or not root_result.success:
            return root_result

        stack.append((self, root_result.node_path, root_result, 0))
        results_map = {id(self): root_result}
        final_result = root_result
        self.logger.debug(f"TreeNode initial results_map: {results_map}")

        # For token aggregation - properly handle None values
        total_input_tokens = getattr(root_result, "input_tokens", None) or 0
        total_output_tokens = getattr(root_result, "output_tokens", None) or 0
        total_cost = getattr(root_result, "cost", None) or 0.0
        total_duration = getattr(root_result, "duration", None) or 0.0
        self.logger.debug(
            f"TreeNode root_result BEFORE child traversal:\n{root_result.display()}"
        )

        while stack:
            node, node_path, node_result, child_idx = stack[-1]

            # Check if this node has a chosen child to follow
            chosen_child_name = None
            if hasattr(node_result, "params") and node_result.params:
                chosen_child_name = node_result.params.get("chosen_child")

            self.logger.info(f"TreeNode Chosen child name: {chosen_child_name}")
            if chosen_child_name:
                # Find the specific child to traverse
                chosen_child = None
                for child in node.children:
                    if child.name == chosen_child_name:
                        chosen_child = child
                        break

                if chosen_child:
                    # Execute the chosen child
                    child_result = chosen_child.execute(user_input, context)
                    node_result.children_results.append(child_result)
                    results_map[id(chosen_child)] = child_result

                    # Aggregate tokens and other metrics - properly handle None values
                    child_input_tokens = (
                        getattr(child_result, "input_tokens", None) or 0
                    )
                    child_output_tokens = (
                        getattr(child_result, "output_tokens", None) or 0
                    )
                    child_cost = getattr(child_result, "cost", None) or 0.0
                    child_duration = getattr(child_result, "duration", None) or 0.0

                    total_input_tokens += child_input_tokens
                    total_output_tokens += child_output_tokens
                    total_cost += child_cost
                    total_duration += child_duration

                    # Update final_result to the most recent child_result
                    final_result = child_result

                    # If no error and child has children, traverse into the chosen child
                    if (
                        not (child_result.error or not child_result.success)
                        and chosen_child.children
                    ):
                        stack.append(
                            (chosen_child, child_result.node_path, child_result, 0)
                        )
                    else:
                        # Move to next sibling or pop
                        stack.pop()
                else:
                    # Chosen child not found, pop from stack
                    stack.pop()
            else:
                # No chosen child, so this is the final node in the path
                # Pop the stack to finish traversal
                stack.pop()

        # Set the aggregated tokens and metrics on the final result
        final_result.input_tokens = total_input_tokens
        final_result.output_tokens = total_output_tokens
        final_result.cost = total_cost
        final_result.duration = total_duration

        return final_result

"""
Splitter node implementation.

This module provides the SplitterNode class which is a node that splits
user input into multiple intent chunks.
"""

from typing import List, Optional
from ..base import TreeNode
from ..enums import NodeType
from ..types import ExecutionResult, ExecutionError
from intent_kit.context import IntentContext


class SplitterNode(TreeNode):
    """Node that splits user input into multiple intent chunks."""

    def __init__(
        self,
        name: Optional[str],
        splitter_function,
        children: List["TreeNode"],
        description: str = "",
        parent: Optional["TreeNode"] = None,
        llm_client=None,
    ):
        super().__init__(
            name=name, description=description, children=children, parent=parent
        )
        self.splitter_function = splitter_function
        self.llm_client = llm_client

    @property
    def node_type(self) -> NodeType:
        """Get the type of this node."""
        return NodeType.SPLITTER

    def execute(
        self, user_input: str, context: Optional[IntentContext] = None
    ) -> ExecutionResult:
        try:
            intent_chunks = self.splitter_function(user_input, debug=False)
            if not intent_chunks:
                self.logger.warning(f"Splitter '{self.name}' found no intent chunks")
                return ExecutionResult(
                    success=False,
                    node_name=self.name,
                    node_path=self.get_path(),
                    node_type=NodeType.SPLITTER,
                    input=user_input,
                    output=None,
                    error=ExecutionError(
                        error_type="NoIntentChunksFound",
                        message="No intent chunks found after splitting",
                        node_name=self.name,
                        node_path=self.get_path(),
                    ),
                    params={"intent_chunks": []},
                    children_results=[],
                )
            self.logger.debug(
                f"Splitter '{self.name}' found {len(intent_chunks)} chunks: {intent_chunks}"
            )
            children_results = []
            all_outputs = []
            for chunk in intent_chunks:
                if isinstance(chunk, dict) and "chunk_text" in chunk:
                    chunk_text = str(chunk["chunk_text"])
                else:
                    chunk_text = str(chunk)
                handled = False
                for child in self.children:
                    try:
                        child_result = child.execute(chunk_text, context)
                        if child_result.success:
                            children_results.append(child_result)
                            all_outputs.append(child_result.output)
                            handled = True
                            break
                    except Exception as e:
                        self.logger.debug(
                            f"Child '{child.name}' failed to handle chunk '{chunk_text}': {e}"
                        )
                        continue
                if not handled:
                    error_result = ExecutionResult(
                        success=False,
                        node_name=f"unhandled_chunk_{chunk_text[:20]}",
                        node_path=self.get_path()
                        + [f"unhandled_chunk_{chunk_text[:20]}"],
                        node_type=NodeType.UNHANDLED_CHUNK,
                        input=chunk_text,
                        output=None,
                        error=ExecutionError(
                            error_type="UnhandledChunk",
                            message=f"No child node could handle chunk: '{chunk_text}'",
                            node_name=self.name,
                            node_path=self.get_path(),
                        ),
                        params={"chunk": chunk_text},
                        children_results=[],
                    )
                    children_results.append(error_result)
            successful_results = [r for r in children_results if r.success]
            overall_success = len(successful_results) > 0
            return ExecutionResult(
                success=overall_success,
                node_name=self.name,
                node_path=self.get_path(),
                node_type=NodeType.SPLITTER,
                input=user_input,
                output=all_outputs if all_outputs else None,
                error=None,
                params={
                    "intent_chunks": intent_chunks,
                    "chunks_processed": len(intent_chunks),
                    "chunks_handled": len(successful_results),
                },
                children_results=children_results,
            )
        except Exception as e:
            self.logger.error(f"Splitter execution error for '{self.name}': {e}")
            return ExecutionResult(
                success=False,
                node_name=self.name,
                node_path=self.get_path(),
                node_type=NodeType.SPLITTER,
                input=user_input,
                output=None,
                error=ExecutionError.from_exception(
                    e, self.name, self.get_path(), node_id=self.node_id
                ),
                params=None,
                children_results=[],
            )

from typing import List, Optional
from ast_node import ASTNode

class FastStack:
    def __init__(self, size: int):
        # Initialize stack with None to simulate fixed size allocation
        self.m_stack: List[Optional[ASTNode]] = [None] * size
        self.m_ptr = -1  # Pointer to the top of the stack

    def push(self, node: ASTNode):
        # Resize if we exceed the current allocation (mirroring vector behavior)
        if self.m_ptr + 1 == len(self.m_stack):
            self.m_stack.append(None)
        
        self.m_ptr += 1
        self.m_stack[self.m_ptr] = node

    def pop(self):
        if self.m_ptr > -1:
            self.m_stack[self.m_ptr] = None  # Clear reference
            self.m_ptr -= 1

    def top(self) -> Optional[ASTNode]:
        if self.m_ptr > -1:
            return self.m_stack[self.m_ptr]
        return None

    def empty(self) -> bool:
        return self.m_ptr == -1

    # Python-specific helper to get the current size (depth) of the stack
    def size(self):
        return self.m_ptr + 1

    # Copy constructor equivalent
    def copy(self) -> 'FastStack':
        new_stack = FastStack(len(self.m_stack))
        new_stack.m_stack = list(self.m_stack)  # Shallow copy of list
        new_stack.m_ptr = self.m_ptr
        return new_stack
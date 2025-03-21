from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID, uuid4
from typing import Tuple, List, Optional
from datetime import datetime
from multiprocessing import Lock
from os import cpu_count

import concurrent.futures as futures
import asyncio

type ID[T: UUID] = T

@dataclass
class Person:
    first: str
    last: str
    child: Optional[None] = None
    child_ptr: Optional[None] = None # This will hold the reference to the child Person
    uuid: ID = field(default_factory=uuid4)

    def __post_init__(self):
        # If a child is provided by name, link it to this instance
        if self.child:
            self.child_ptr = None  # To start without a direct reference until explicitly set

    def add_child(self, child: 'Person'):
        self.child_ptr = child

    def __str__(self):
        return f"{self.first} {self.last}, UUID: {self.uuid}"

    def iterate_children(self):
        # Return the current person and all its children in a linked list style
        current = self
        while current:
            yield current
            current = current.child_ptr
    
def test_rust_iterator(idx, objs):
    # RUST CODE LATER
    # Simulating processing of customer information (like iterating over customers in Rust)
    return [idx, [str(obj) for obj in objs]]  # Collecting the string representation of each person
        
def main_example():
    # Create person objects
    alice_clone = Person("Alice", "Clone")
    alicia = Person("Alice", "Marcus", child="Alice Clone")
    james = Person("James", "Marcus", child="Alicia Marcus")
    
    # Creating a hierarchy by setting child pointers
    alice_clone.add_child(alicia)
    alicia.add_child(james)
    
    # Collect all persons in a list
    objs = [james, alicia, alice_clone]
    
    # Running thread pool for simulating concurrent processing
    with futures.ThreadPoolExecutor(max_workers=cpu_count()) as executor:
        # Submitting tasks to thread pool
        futures_res = [executor.submit(test_rust_iterator, idx, objs) for idx in range(1, len(objs) + 1)]
        
        for future in futures.as_completed(futures_res):
            idx, result = future.result()
            print(f"Thread {idx} came back with the following:")
            print("\n\t".join(result))

if __name__ == "__main__":
    main_example()

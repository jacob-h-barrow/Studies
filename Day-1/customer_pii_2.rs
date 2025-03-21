use std::sync::Arc;
use std::hash::{Hash, Hasher};
use std::collections::hash_map::DefaultHasher;
use std::fmt;
use std::thread;

struct CustomerPII {
    first_name: String,
    last_name: String,
    uuid: String,
    child: Option<Arc<CustomerPII>>, // Use `Arc` for safe shared ownership
}

impl CustomerPII {
    fn new(first_name: &str, last_name: &str, uuid: &str) -> Arc<Self> {
        Arc::new(CustomerPII {
            first_name: first_name.to_string(),
            last_name: last_name.to_string(),
            uuid: uuid.to_string(),
            child: None,
        })
    }

    fn with_child(parent: &Arc<Self>, child: Arc<Self>) -> Arc<Self> {
        // Create a new instance with the child added
        Arc::new(CustomerPII {
            first_name: parent.first_name.clone(),
            last_name: parent.last_name.clone(),
            uuid: parent.uuid.clone(),
            child: Some(child),
        })
    }
}

impl fmt::Display for CustomerPII {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "Customer: {} {}, UUID: {}",
            self.first_name, self.last_name, self.uuid
        )
    }
}

// Implement `Hash`
impl Hash for CustomerPII {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.uuid.hash(state); // Only hash the UUID
    }
}

// Implement `PartialEq` and `Eq`
impl PartialEq for CustomerPII {
    fn eq(&self, other: &Self) -> bool {
        self.uuid == other.uuid
    }
}

impl Eq for CustomerPII {}

// Iterator implementation
struct CustomerIterator {
    current: Option<Arc<CustomerPII>>,
}

impl Iterator for CustomerIterator {
    type Item = Arc<CustomerPII>;

    fn next(&mut self) -> Option<Self::Item> {
        self.current.take().map(|node| {
            let next_child = node.child.clone();
            self.current = next_child;
            node
        })
    }
}

impl CustomerPII {
    fn iter(self: Arc<Self>) -> CustomerIterator {
        CustomerIterator {
            current: Some(self),
        }
    }
}

// Main function for testing
fn main() {
    let parent = CustomerPII::new("Alice", "Doe", "123");
    let child1 = CustomerPII::new("Bob", "Doe", "456");
    let child2 = CustomerPII::new("Charlie", "Doe", "789");

    // Construct the hierarchy immutably
    let parent = CustomerPII::with_child(&parent, child1.clone());
    let parent = CustomerPII::with_child(&parent, child2.clone()); // Updated to parent instead of child1

    println!("Iterating over Customer Chain in the Main Thread:");
    for customer in parent.clone().iter() {
        println!("{}", customer);
    }

    // Spawn a thread to iterate
    let parent_clone = parent.clone();
    let handle = thread::spawn(move || {
        println!("\nIterating in a New Thread:");
        for customer in parent_clone.iter() {
            println!("{}", customer);
        }
    });

    handle.join().unwrap();
}


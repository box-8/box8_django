// Initialize the diagram
let myDiagram;
const agents = new Map(); // Store agents for easy reference
let selectedNode = null; // Track the currently selected node
let selectedLink = null; // Track the currently selected link

const RELATIONSHIP_TYPES = [
    { text: "Collaborates with", value: "collaborates" },
    { text: "Supervises", value: "supervises" },
    { text: "Assists", value: "assists" },
    { text: "Delegates to", value: "delegates" }
];

// Initialize GoJS
function init() {
    const $ = go.GraphObject.make;
    myDiagram = $(go.Diagram, "diagramDiv", {
        initialContentAlignment: go.Spot.Center,
        "undoManager.isEnabled": true,
        layout: $(go.ForceDirectedLayout),
        // Enable linking
        "linkingTool.direction": go.LinkingTool.ForwardsOnly,
        "linkingTool.portGravity": 20,
        // Show context menu for links
        "contextMenuTool.showContextMenu": true,
        model: $(go.GraphLinksModel, {
            nodeDataArray: [],
            linkDataArray: []
        })
    });

    // Define node template
    myDiagram.nodeTemplate =
        $(go.Node, "Auto",
            {
                selectionAdorned: true,
                resizable: true,
                layoutConditions: go.Part.LayoutStandard & ~go.Part.LayoutNodeSized,
                // Enable linking from/to this node
                fromLinkable: true,
                toLinkable: true,
                // Handle selection changed
                selectionChanged: onNodeSelectionChanged
            },
            $(go.Shape, "RoundedRectangle", {
                fill: "white",
                strokeWidth: 2,
                stroke: "#007bff",
                portId: "",  // this Shape is the Node's port
                cursor: "pointer"
            }),
            $(go.Panel, "Vertical",
                { margin: 8 },
                $(go.TextBlock, {
                        margin: 8,
                        font: "bold 14px sans-serif"
                    },
                    new go.Binding("text", "name")
                ),
                $(go.TextBlock, {
                        margin: 8,
                        font: "12px sans-serif"
                    },
                    new go.Binding("text", "role")
                ),
                $(go.TextBlock, {
                        margin: 8,
                        font: "italic 11px sans-serif",
                        wrap: go.TextBlock.WrapFit,
                        width: 150
                    },
                    new go.Binding("text", "goal")
                ),
                $(go.TextBlock, {
                        margin: 8,
                        font: "10px sans-serif",
                        stroke: "#666",
                        visible: false
                    },
                    new go.Binding("text", "file", function(file) { return file ? " " + file.split('/').pop() : ""; }),
                    new go.Binding("visible", "file", function(file) { return !!file; })
                )
            )
        );

    // Define link template with relationship type label and context menu
    myDiagram.linkTemplate =
        $(go.Link,
            {
                routing: go.Link.AvoidsNodes,
                corner: 5,
                selectionAdorned: true,
                selectionChanged: onLinkSelectionChanged,
                // Add tooltip to show description and expected output
                toolTip: $(go.Adornment, "Auto",
                    $(go.Shape, { fill: "#FFFFCC" }),
                    $(go.Panel, "Vertical",
                        { margin: 3 },
                        $(go.TextBlock, { margin: 4, font: "bold 10px sans-serif" },
                            new go.Binding("text", "", function(data) {
                                return data.description ? "Description: " + data.description : "";
                            })),
                        $(go.TextBlock, { margin: 4, font: "10px sans-serif" },
                            new go.Binding("text", "", function(data) {
                                return data.expected_output ? "Expected Output: " + data.expected_output : "";
                            }))
                    )
                ),
                contextMenu: $(go.Adornment, "Vertical",
                    ...RELATIONSHIP_TYPES.map(type =>
                        $(go.TextBlock, type.text, {
                            margin: 3,
                            click: (e, obj) => updateLinkRelationship(e, obj, type.value)
                        })
                    )
                )
            },
            $(go.Shape, { strokeWidth: 2 }),
            $(go.Shape, { toArrow: "Standard" }),
            $(go.Panel, "Auto",
                $(go.Shape, "Rectangle", { fill: "white", stroke: null }),
                $(go.TextBlock, {
                    margin: 5,
                    font: "11px sans-serif",
                    background: "white"
                },
                new go.Binding("text", "relationship", function(relationship) {
                    return RELATIONSHIP_TYPES.find(t => t.value === relationship)?.text || relationship;
                }))
            )
        );

    // Handle link creation
    myDiagram.addDiagramListener("LinkDrawn", e => {
        const link = e.subject;
        if (link instanceof go.Link) {
            // Set default relationship type
            myDiagram.model.setDataProperty(link.data, "relationship", "collaborates");
            // Show context menu
            const contextmenu = link.findObject("ContextMenu");
            if (contextmenu) {
                const diagram = link.diagram;
                contextmenu.visible = true;
                const pt = diagram.lastInput.viewPoint;
                contextmenu.position = new go.Point(pt.x + 10, pt.y + 10);
            }
        }
    });

    // Handle background click to clear selection
    myDiagram.addDiagramListener("BackgroundSingleClicked", e => {
        resetAgentForm();
        resetRelationshipForm();
    });
}

// Function to handle node selection changes
function onNodeSelectionChanged(node) {
    if (node.isSelected) {
        selectedNode = node;
        populateAgentForm(node.data);
        updateFormToEditMode();
        const modal = new bootstrap.Modal(document.getElementById('agentModal'));
        modal.show();
    } else {
        if (selectedNode === node) {
            selectedNode = null;
            resetAgentForm();
        }
    }
}

// Function to handle link selection changes
function onLinkSelectionChanged(link) {
    if (link.isSelected) {
        selectedLink = link;
        populateRelationshipForm(link.data);
        updateRelationshipFormToEditMode();
        const modal = new bootstrap.Modal(document.getElementById('taskModal'));
        modal.show();
    } else {
        if (selectedLink === link) {
            selectedLink = null;
            resetRelationshipForm();
        }
    }
}

// Function to populate the agent form with selected node data
function populateAgentForm(data) {
    document.getElementById("agentName").value = data.name || "";
    document.getElementById("agentRole").value = data.role || "";
    document.getElementById("agentGoal").value = data.goal || "";
    document.getElementById("agentBackstory").value = data.backstory || "";
    document.getElementById("agentFile").value = data.file || "";
}

// Function to update form to edit mode
function updateFormToEditMode() {
    const submitBtn = document.getElementById("agentSubmitBtn");
    const cancelBtn = document.getElementById("agentCancelBtn");
    const deleteBtn = document.getElementById("agentDeleteBtn");
    
    submitBtn.textContent = "Update Agent";
    cancelBtn.style.display = "block";
    deleteBtn.style.display = "block";
}

// Function to reset the agent form
function resetAgentForm() {
    document.getElementById("agentForm").reset();
    selectedNode = null;
    document.getElementById("agentSubmitBtn").textContent = "Add Agent";
    document.getElementById("agentCancelBtn").style.display = "none";
    document.getElementById("agentDeleteBtn").style.display = "none";
}

// Function to populate the relationship form with selected link data
function populateRelationshipForm(data) {
    document.getElementById("fromAgent").value = data.from || "";
    document.getElementById("toAgent").value = data.to || "";
    document.getElementById("relationshipType").value = data.relationship || "";
    document.getElementById("relationshipDescription").value = data.description || "";
    document.getElementById("relationshipExpectedOutput").value = data.expected_output || "";
}

// Function to update relationship form to edit mode
function updateRelationshipFormToEditMode() {
    const submitBtn = document.getElementById("relationshipSubmitBtn");
    const cancelBtn = document.getElementById("relationshipCancelBtn");
    const deleteBtn = document.getElementById("relationshipDeleteBtn");
    
    submitBtn.textContent = "Update Task";
    cancelBtn.style.display = "block";
    deleteBtn.style.display = "block";
}

// Function to reset the relationship form
function resetRelationshipForm() {
    const form = document.getElementById("relationshipForm");
    const submitBtn = document.getElementById("relationshipSubmitBtn");
    const cancelBtn = document.getElementById("relationshipCancelBtn");
    const deleteBtn = document.getElementById("relationshipDeleteBtn");
    form.reset();
    submitBtn.textContent = "Add Relationship";
    submitBtn.classList.remove("btn-success");
    submitBtn.classList.add("btn-primary");
    cancelBtn.style.display = "none";
    deleteBtn.style.display = "none";
    selectedLink = null;
}

// Function to update link relationship
function updateLinkRelationship(e, obj, value) {
    const diagram = obj.part.diagram;
    const link = obj.part.adornedPart;
    diagram.startTransaction("update relationship");
    diagram.model.setDataProperty(link.data, "relationship", value);
    diagram.commitTransaction("update relationship");
    // Update layout when relationship type changes
    diagram.layoutDiagram(true);
}

// Function to delete a relationship
function deleteRelationship(link) {
    myDiagram.startTransaction("delete relationship");
    myDiagram.model.removeLinkData(link.data);
    myDiagram.commitTransaction("delete relationship");
    resetRelationshipForm();
    myDiagram.layoutDiagram(true);
    ensureAllAgentsVisible();
}

// Function to delete an agent and its relationships
function deleteAgentAndRelationships(agentKey) {
    myDiagram.startTransaction("delete agent");
    
    // Find all relationships connected to this agent
    const relationsToDelete = myDiagram.model.linkDataArray.filter(link => 
        link.from === agentKey || link.to === agentKey
    );
    
    // Delete all connected relationships
    relationsToDelete.forEach(link => {
        myDiagram.model.removeLinkData(link);
    });
    
    // Delete the agent
    myDiagram.model.removeNodeData(myDiagram.model.findNodeDataForKey(agentKey));
    
    // Remove from agents map
    agents.delete(agentKey);
    
    myDiagram.commitTransaction("delete agent");
    
    // Update dropdowns
    updateAgentDropdowns();
    
    // Reset form
    resetAgentForm();
    
    // Update layout and ensure all agents are visible
    myDiagram.layoutDiagram(true);
    ensureAllAgentsVisible();
}

// Update agent dropdowns
function updateAgentDropdowns() {
    const fromSelect = document.getElementById("fromAgent");
    const toSelect = document.getElementById("toAgent");
    
    // Clear existing options
    fromSelect.innerHTML = "";
    toSelect.innerHTML = "";
    
    // Add agents to dropdowns
    agents.forEach((agent, key) => {
        const fromOption = new Option(agent.name, key);
        const toOption = new Option(agent.name, key);
        fromSelect.add(fromOption);
        toSelect.add(toOption);
    });
}

// Function to ensure all agents are visible
function ensureAllAgentsVisible() {
    // Add a small delay to let the layout stabilize
    setTimeout(() => {
        myDiagram.scale = 1.0; // Reset zoom level
        myDiagram.zoomToFit(); // Zoom to fit all content
        
        // Add a bit of padding around the content
        const padding = 50;
        const bounds = myDiagram.documentBounds.copy().inflate(padding);
        myDiagram.centerRect(bounds);
    }, 100);
}

// Function to save diagram as JSON
function saveDiagram() {
    const diagramData = {
        nodes: myDiagram.model.nodeDataArray,
        links: myDiagram.model.linkDataArray
    };
    
    const jsonString = JSON.stringify(diagramData, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = 'crew-ai-diagram.json';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// Function to load diagram from JSON
function loadDiagram(file) {
    const reader = new FileReader();
    reader.onload = function(event) {
        try {
            const diagramData = JSON.parse(event.target.result);
            
            // Clear existing diagram
            myDiagram.model.nodeDataArray = [];
            myDiagram.model.linkDataArray = [];
            agents.clear();
            
            // Load nodes first
            diagramData.nodes.forEach(node => {
                agents.set(node.key, node);
                myDiagram.model.addNodeData(node);
            });
            
            // Then load relationships
            diagramData.links.forEach(link => {
                myDiagram.model.addLinkData(link);
            });
            
            // Update UI
            updateAgentDropdowns();
            myDiagram.layoutDiagram(true);
            ensureAllAgentsVisible();
            
        } catch (error) {
            alert('Error loading diagram: Invalid file format');
            console.error('Error loading diagram:', error);
        }
    };
    reader.readAsText(file);
}

// Handle form submission for agents
document.getElementById("agentForm").addEventListener("submit", function(e) {
    e.preventDefault();
    
    const name = document.getElementById("agentName").value;
    const role = document.getElementById("agentRole").value;
    const goal = document.getElementById("agentGoal").value;
    const backstory = document.getElementById("agentBackstory").value;
    const file = document.getElementById("agentFile").value;

    const agentData = {
        name: name,
        role: role,
        goal: goal,
        backstory: backstory,
        file: file
    };

    if (selectedNode) {
        // Update existing agent
        myDiagram.startTransaction("update agent");
        const data = selectedNode.data;
        Object.assign(data, agentData);
        myDiagram.model.updateTargetBindings(data);
        agents.set(data.key, data);
        myDiagram.commitTransaction("update agent");
        resetAgentForm();
        myDiagram.layoutDiagram(true);
        ensureAllAgentsVisible();
    } else {
        // Create new agent
        agentData.key = Date.now().toString();
        agents.set(agentData.key, agentData);
        myDiagram.model.addNodeData(agentData);
        myDiagram.layoutDiagram(true);
        ensureAllAgentsVisible();
    }
    
    // Update dropdowns
    updateAgentDropdowns();

    // Reset form
    resetAgentForm();
});

// Handle cancel button click
document.getElementById("agentCancelBtn").addEventListener("click", function(e) {
    e.preventDefault();
    resetAgentForm();
    myDiagram.clearSelection();
});

// Handle agent delete button click
document.getElementById("agentDeleteBtn").addEventListener("click", function(e) {
    e.preventDefault();
    if (selectedNode) {
        if (confirm("Are you sure you want to delete this agent? All relationships connected to this agent will also be deleted.")) {
            deleteAgentAndRelationships(selectedNode.data.key);
        }
    }
});

// Handle form submission for relationships
document.getElementById("relationshipForm").addEventListener("submit", function(e) {
    e.preventDefault();
    
    const fromKey = document.getElementById("fromAgent").value;
    const toKey = document.getElementById("toAgent").value;
    const relationshipType = document.getElementById("relationshipType").value;
    const description = document.getElementById("relationshipDescription").value;
    const expected_output = document.getElementById("relationshipExpectedOutput").value;

    // Don't create self-relationships
    if (fromKey === toKey) {
        alert("An agent cannot have a relationship with itself");
        return;
    }

    const relationshipData = {
        from: fromKey,
        to: toKey,
        relationship: relationshipType,
        description: description,
        expected_output: expected_output
    };

    if (selectedLink) {
        // Update existing relationship
        myDiagram.startTransaction("update relationship");
        const data = selectedLink.data;
        Object.assign(data, relationshipData);
        myDiagram.model.updateTargetBindings(data);
        myDiagram.commitTransaction("update relationship");
        resetRelationshipForm();
        myDiagram.layoutDiagram(true);
        ensureAllAgentsVisible();
    } else {
        // Create new relationship
        myDiagram.model.addLinkData(relationshipData);
        myDiagram.layoutDiagram(true);
        ensureAllAgentsVisible();
    }

    // Reset form
    resetRelationshipForm();
});

// Handle relationship cancel button click
document.getElementById("relationshipCancelBtn").addEventListener("click", function(e) {
    e.preventDefault();
    resetRelationshipForm();
    myDiagram.clearSelection();
});

// Handle relationship delete button click
document.getElementById("relationshipDeleteBtn").addEventListener("click", function(e) {
    e.preventDefault();
    if (selectedLink) {
        if (confirm("Are you sure you want to delete this relationship?")) {
            deleteRelationship(selectedLink);
        }
    }
});

// Initialize diagram when page loads
window.addEventListener('DOMContentLoaded', function() {
    init();
    
    // Add save button handler
    document.getElementById('saveButton').addEventListener('click', function(e) {
        e.preventDefault();
        saveDiagram();
    });
    
    // Add load button handler
    document.getElementById('loadButton').addEventListener('change', function(e) {
        if (this.files && this.files[0]) {
            if (confirm('Loading a new diagram will replace the current one. Are you sure you want to continue?')) {
                loadDiagram(this.files[0]);
            }
            this.value = ''; // Reset file input
        }
    });
});

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
            nodeDataArray: [
                { key: "output", role: "Output", goal: "output", category: "output" }
            ],
            linkDataArray: []
        })
    });

    // Define output node template
    myDiagram.nodeTemplateMap.add("output",
        $(go.Node, "Auto",
            {
                selectionAdorned: true,
                fromLinkable: false,
                toLinkable: true
            },
            $(go.Shape, "Circle",
                {
                    fill: "white",
                    stroke: "green",
                    strokeWidth: 2,
                    width: 60,
                    height: 60
                }
            ),
            $(go.TextBlock,
                { margin: 8 },
                new go.Binding("text", "role")
            )
        )
    );

    // Define node template
    myDiagram.nodeTemplate =
        $(go.Node, "Auto",
            {
                selectionAdorned: true,
                resizable: true,
                layoutConditions: go.Part.LayoutStandard & ~go.Part.LayoutNodeSized,
                fromLinkable: true,
                toLinkable: true,
                selectionChanged: onNodeSelectionChanged
            },
            // Add tooltip to show all agent properties
            {
                toolTip: $(go.Adornment, "Auto",
                    $(go.Shape, { fill: "#FFFFCC", stroke: "#666", strokeWidth: 0.5 }),
                    $(go.Panel, "Vertical",
                        { margin: 6 },
                        // Title - Agent Name
                        $(go.TextBlock,
                            {
                                margin: new go.Margin(0, 0, 4, 0),
                                font: "bold 12px sans-serif",
                                stroke: "#333"
                            },
                            new go.Binding("text", "name")
                        ),
                        // Role
                        $(go.Panel, "Horizontal",
                            { alignment: go.Spot.Left },
                            $(go.TextBlock, "Role: ",
                                {
                                    font: "bold 10px sans-serif",
                                    stroke: "#666"
                                }
                            ),
                            $(go.TextBlock,
                                { font: "10px sans-serif", stroke: "#333" },
                                new go.Binding("text", "role")
                            )
                        ),
                        // Goal
                        $(go.Panel, "Vertical",
                            { alignment: go.Spot.Left },
                            $(go.TextBlock, "Goal:",
                                {
                                    font: "bold 10px sans-serif",
                                    stroke: "#666",
                                    margin: new go.Margin(4, 0, 2, 0)
                                }
                            ),
                            $(go.TextBlock,
                                {
                                    font: "10px sans-serif",
                                    stroke: "#333",
                                    width: 200,
                                    wrap: go.TextBlock.WrapFit,
                                    margin: new go.Margin(0, 0, 0, 8)
                                },
                                new go.Binding("text", "goal", function(goal) {
                                    return goal || "No goal specified";
                                })
                            )
                        ),
                        // Backstory
                        $(go.Panel, "Vertical",
                            { alignment: go.Spot.Left },
                            $(go.TextBlock, "Backstory:",
                                {
                                    font: "bold 10px sans-serif",
                                    stroke: "#666",
                                    margin: new go.Margin(4, 0, 2, 0)
                                }
                            ),
                            $(go.TextBlock,
                                {
                                    font: "10px sans-serif",
                                    stroke: "#333",
                                    width: 200,
                                    wrap: go.TextBlock.WrapFit,
                                    margin: new go.Margin(0, 0, 0, 8)
                                },
                                new go.Binding("text", "backstory", function(backstory) {
                                    return backstory || "No backstory provided";
                                })
                            )
                        ),
                        // Associated File
                        $(go.Panel, "Horizontal",
                            { 
                                alignment: go.Spot.Left,
                                margin: new go.Margin(4, 0, 0, 0)
                            },
                            $(go.TextBlock, "File: ",
                                {
                                    font: "bold 10px sans-serif",
                                    stroke: "#666"
                                }
                            ),
                            $(go.TextBlock,
                                { 
                                    font: "10px sans-serif",
                                    stroke: "#333"
                                },
                                new go.Binding("text", "file", function(file) {
                                    return file ? file.split('/').pop() : "No file associated";
                                })
                            )
                        )
                    )
                )
            },
            $(go.Shape, "RoundedRectangle", {
                fill: "white",
                strokeWidth: 2,
                stroke: "#007bff",
                portId: "",
                cursor: "pointer"
            }),
            $(go.Panel, "Vertical",
                { margin: 8 },
                // Agent Name as title
                $(go.TextBlock, {
                    margin: 8,
                    font: "bold 14px sans-serif"
                },
                new go.Binding("text", "name")),
                // Role
                $(go.TextBlock, {
                    margin: 8,
                    font: "12px sans-serif"
                },
                new go.Binding("text", "role")),
                // Goal
                $(go.TextBlock, {
                    margin: 8,
                    font: "italic 11px sans-serif",
                    wrap: go.TextBlock.WrapFit,
                    width: 150
                },
                new go.Binding("text", "goal")),
                // Backstory
                $(go.TextBlock, {
                    margin: 8,
                    font: "11px sans-serif",
                    wrap: go.TextBlock.WrapFit,
                    width: 150,
                    stroke: "#666"
                },
                new go.Binding("text", "backstory")),
                // File
                $(go.TextBlock, {
                    margin: 8,
                    font: "10px sans-serif",
                    stroke: "#666"
                },
                new go.Binding("text", "file", function(file) {
                    return file ? "📄 " + file.split('/').pop() : "";
                }))
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
                // Add tooltip to show all relationship properties
                toolTip: $(go.Adornment, "Auto",
                    $(go.Shape, { fill: "#FFFFCC", stroke: "#666", strokeWidth: 0.5 }),
                    $(go.Panel, "Vertical",
                        { margin: 6 },
                        // Title - Relationship Type
                        $(go.TextBlock, 
                            { 
                                margin: new go.Margin(0, 0, 4, 0),
                                font: "bold 12px sans-serif",
                                stroke: "#333"
                            },
                            new go.Binding("text", "relationship", function(rel) {
                                return RELATIONSHIP_TYPES.find(t => t.value === rel)?.text || rel;
                            })
                        ),
                        // From Agent
                        $(go.Panel, "Horizontal",
                            { alignment: go.Spot.Left },
                            $(go.TextBlock, "From: ", 
                                { 
                                    font: "bold 10px sans-serif",
                                    stroke: "#666"
                                }
                            ),
                            $(go.TextBlock,
                                { font: "10px sans-serif", stroke: "#333" },
                                new go.Binding("text", "from")
                            )
                        ),
                        // To Agent
                        $(go.Panel, "Horizontal",
                            { alignment: go.Spot.Left },
                            $(go.TextBlock, "To: ", 
                                { 
                                    font: "bold 10px sans-serif",
                                    stroke: "#666"
                                }
                            ),
                            $(go.TextBlock,
                                { font: "10px sans-serif", stroke: "#333" },
                                new go.Binding("text", "to")
                            )
                        ),
                        // Description
                        $(go.Panel, "Vertical",
                            { alignment: go.Spot.Left, visible: true },
                            $(go.TextBlock, "Description:", 
                                { 
                                    font: "bold 10px sans-serif",
                                    stroke: "#666",
                                    margin: new go.Margin(4, 0, 2, 0)
                                }
                            ),
                            $(go.TextBlock,
                                { 
                                    font: "10px sans-serif",
                                    stroke: "#333",
                                    width: 200,
                                    wrap: go.TextBlock.WrapFit,
                                    margin: new go.Margin(0, 0, 0, 8)
                                },
                                new go.Binding("text", "description", function(desc) {
                                    return desc || "No description provided";
                                })
                            )
                        ),
                        // Expected Output
                        $(go.Panel, "Vertical",
                            { alignment: go.Spot.Left, visible: true },
                            $(go.TextBlock, "Expected Output:", 
                                { 
                                    font: "bold 10px sans-serif",
                                    stroke: "#666",
                                    margin: new go.Margin(4, 0, 2, 0)
                                }
                            ),
                            $(go.TextBlock,
                                { 
                                    font: "10px sans-serif",
                                    stroke: "#333",
                                    width: 200,
                                    wrap: go.TextBlock.WrapFit,
                                    margin: new go.Margin(0, 0, 0, 8)
                                },
                                new go.Binding("text", "expected_output", function(output) {
                                    return output || "No expected output specified";
                                })
                            )
                        )
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
                    background: "white",
                    maxLines: 2,
                    width: 150,
                    wrap: go.TextBlock.WrapFit,
                    stroke: "#666"
                },
                new go.Binding("text", "", function(data) {
                    return data.description || "No description";
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
    fromSelect.innerHTML = '<option value="">Select agent...</option>';
    toSelect.innerHTML = '<option value="">Select agent...</option>';
    
    // Add agents to dropdowns
    const nodes = myDiagram.model.nodeDataArray;
    nodes.forEach(node => {
        const fromOption = new Option(node.role, node.key);
        const toOption = new Option(node.role, node.key);
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

// Function to load diagram from JSON loadJsonFile
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

// Function to save the current diagram to the server
function saveCurrentDiagram() {
    const diagramName = document.getElementById('diagramNameInput').value.trim();
    if (!diagramName) {
        alert('Please enter a name for the diagram.');
        return;
    }
    const diagramData = {
        nodes: myDiagram.model.nodeDataArray,
        links: myDiagram.model.linkDataArray
    };
    fetch('/chatapp/designer/save-diagram/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            name: diagramName,
            diagram: JSON.stringify(diagramData)
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Diagram saved successfully!');
            fetchAndDisplayJsonFiles();
        } else {
            alert('Error saving diagram: ' + data.error);
        }
    })
    .catch(error => console.error('Error saving diagram:', error));
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

// Function to load diagram from JSON loadJsonFile
function loadJsonFile(fileName) {
    fetch(`/chatapp/designer/json-files/${fileName}`)
        .then(response => response.json())
        .then(diagramData => {
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
        })
        .catch(error => console.error('Error loading JSON file:', error));
}

// Function to fetch JSON files and populate the modal
function fetchAndDisplayJsonFiles() {
    fetch('/chatapp/designer/json-files') // Assuming a backend endpoint exists
        .then(response => response.json())
        .then(files => {
            const fileList = document.getElementById('jsonFileList');
            fileList.innerHTML = '';
            files.forEach(file => {
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item';
                listItem.textContent = file;
                listItem.onclick = () => {
                    loadJsonFile(file);
                    document.getElementById('diagramNameInput').value = file;
                };
                fileList.appendChild(listItem);
            });
        })
        .catch(error => console.error('Error fetching JSON files:', error));
}

// Attach event listener to modal show event
const jsonFilesModal = document.getElementById('jsonFilesModal');
if (jsonFilesModal) {
    jsonFilesModal.addEventListener('show.bs.modal', fetchAndDisplayJsonFiles);
}

// Event listener for save button
const saveButton = document.getElementById('saveCurrentDiagram');
if (saveButton) {
    saveButton.addEventListener('click', saveCurrentDiagram);
}

// Function to clear and reset the diagram
function clearCurrentDiagram() {
    myDiagram.model.nodeDataArray = [];
    myDiagram.model.linkDataArray = [];
    agents.clear();
    // Add default output node
    const outputNode = { key: "output", role: "Output", goal: "output", category: "output" };
    myDiagram.model.addNodeData(outputNode);
    agents.set(outputNode.key, outputNode);
    updateAgentDropdowns();
    myDiagram.layoutDiagram(true);
    ensureAllAgentsVisible();
    document.getElementById('diagramNameInput').value = '';
}

// Event listener for clear button
const clearButton = document.getElementById('clearCurrentDiagram');
if (clearButton) {
    clearButton.addEventListener('click', clearCurrentDiagram);
}

// Function to delete the current diagram
function deleteCurrentDiagram() {
    const diagramName = document.getElementById('diagramNameInput').value.trim();
    if (!diagramName) {
        alert('Please enter the name of the diagram to delete.');
        return;
    }
    if (!confirm(`Are you sure you want to delete the diagram: ${diagramName}?`)) {
        return;
    }
    fetch(`/chatapp/designer/delete-diagram/${encodeURIComponent(diagramName)}`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Diagram deleted successfully!');
            fetchAndDisplayJsonFiles(); // Refresh the list
            clearCurrentDiagram(); // Clear the diagram from the canvas
        } else {
            alert('Error deleting diagram: ' + data.error);
        }
    })
    .catch(error => console.error('Error deleting diagram:', error));
}

// Event listener for delete button
const deleteButton = document.getElementById('deleteCurrentDiagram');
if (deleteButton) {
    deleteButton.addEventListener('click', deleteCurrentDiagram);
}

// Handle form submission for agents
document.getElementById("agentForm").addEventListener("submit", function(e) {
    e.preventDefault();
    
    const role = document.getElementById("agentRole").value;
    const goal = document.getElementById("agentGoal").value;
    const backstory = document.getElementById("agentBackstory").value;
    const file = document.getElementById("agentFile").value;

    const agentData = {
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
        myDiagram.layoutDiagram(true);
        ensureAllAgentsVisible();
        // Keep the form in edit mode
        updateFormToEditMode();
    } else {
        // Create new agent
        agentData.key = Date.now().toString();
        agents.set(agentData.key, agentData);
        myDiagram.model.addNodeData(agentData);
        myDiagram.layoutDiagram(true);
        ensureAllAgentsVisible();
        // Reset form for new entries
        resetAgentForm();
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
const taskForm = document.getElementById("relationshipForm");
const fromInput = document.getElementById("fromAgent");
const toInput = document.getElementById("toAgent");

// Update canvas when from/to attributes change
fromInput.addEventListener("change", updateCanvas);
toInput.addEventListener("change", updateCanvas);

function updateCanvas() {
    const fromValue = fromInput.value;
    const toValue = toInput.value;
    // Logic to update the diagram based on new from/to values
    const linkData = myDiagram.model.linkDataArray.find(link => link.from === fromValue && link.to === toValue);
    if (linkData) {
        myDiagram.model.updateTargetBindings(linkData);
    }
    myDiagram.layoutDiagram(true);
}

taskForm.addEventListener("submit", function(e) {
    e.preventDefault();
    
    const fromKey = document.getElementById("fromAgent").value;
    const toKey = document.getElementById("toAgent").value;
    const relationshipType = document.getElementById("relationshipType").value;
    const description = document.getElementById("relationshipDescription").value;
    const expected_output = document.getElementById("relationshipExpectedOutput").value;

    if (selectedLink) {
        // Update existing relationship
        myDiagram.startTransaction("update relationship");
        const data = selectedLink.data;
        Object.assign(data, {
            from: fromKey,
            to: toKey,
            relationship: relationshipType,
            description: description,
            expected_output: expected_output
        });
        myDiagram.model.updateTargetBindings(data);
        myDiagram.commitTransaction("update relationship");
        // Keep the form in edit mode
        updateRelationshipFormToEditMode();
    } else {
        // Create new relationship
        const linkData = {
            from: fromKey,
            to: toKey,
            relationship: relationshipType,
            description: description,
            expected_output: expected_output
        };
        myDiagram.model.addLinkData(linkData);
        // Reset form for new entries
        resetRelationshipForm();
    }
    
    myDiagram.layoutDiagram(true);
    ensureAllAgentsVisible();
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
window.onload = function() {
    init();
    fetchAndDisplayJsonFiles();
    
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
};

// Helper function to get CSRF token
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

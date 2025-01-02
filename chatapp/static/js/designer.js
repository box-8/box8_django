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

let isCtrlPressed = false;

const agentForm = document.getElementById("agentForm");
// Handle form submission for relationships
const taskForm = document.getElementById("relationshipForm");
const fromInput = document.getElementById("fromAgent");
const toInput = document.getElementById("toAgent");

// Update canvas when from/to attributes change
fromInput.addEventListener("change", relationUpdateFromTo);
toInput.addEventListener("change", relationUpdateFromTo);


let linkDataCurrent = null;
let toInputpreviousValue = toInput.value
let fromInputpreviousValue = fromInput.value;
function focusFromTo(){
    toInputpreviousValue = toInput.value;
    fromInputpreviousValue = fromInput.value;
    linkDataCurrent = myDiagram.model.linkDataArray.find(link => link.from === fromInputpreviousValue && link.to === toInputpreviousValue);
    
    return linkDataCurrent
}
toInput.addEventListener("focus", () => {
    focusFromTo()
});
fromInput.addEventListener("focus", () => {
    focusFromTo()
});

// Add swap relationship button handler
const swapRelationBtn = document.getElementById('swapRelationBtn');
swapRelationBtn.addEventListener('click', function() {
    focusFromTo()
    const fromValue = fromInput.value;   
    const toValue = toInput.value;
    // Swap values
    fromInput.value = toValue;
    toInput.value = fromValue;
    relationUpdateFromTo()
});


function relationUpdateFromTo() {
    const fromValue = fromInput.value;
    const toValue = toInput.value;
    // Logic to update the diagram based on new from/to values
    linkDataCurrent.from = fromValue;
    linkDataCurrent.to = toValue;
    if (linkDataCurrent) {
        myDiagram.model.updateTargetBindings(linkDataCurrent);
    }
    
    linkDataCurrent = myDiagram.model.linkDataArray.find(link => link.from === fromValue && link.to === toValue);
    
    // console.log(linkDataCurrent)
    redrawRelationships()    
}


function redrawRelationships() {
    // Clear existing relationships
    diagramData = DiagramData()
    myDiagram.model.linkDataArray = [];

    // Then load relationships
    diagramData.links.forEach(link => {
        myDiagram.model.addLinkData(link);
    });
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Control') {
        isCtrlPressed = true;
        myDiagram.nodes.each(node => node.fromLinkable = isCtrlPressed);
    }
    if (e.key === 'Delete' && myDiagram.selection.count > 0) {
        myDiagram.selection.each(part => {
            if (part instanceof go.Link) {
                myDiagram.remove(part);
            }
        });
    }
});

document.addEventListener('keyup', (e) => {
    if (e.key === 'Control') {
        isCtrlPressed = false;
        myDiagram.nodes.each(node => node.fromLinkable = isCtrlPressed);
    }
});

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
                movable: true,
                layoutConditions: go.Part.LayoutStandard & ~go.Part.LayoutNodeSized,
                fromLinkable: false,  // Default to false
                toLinkable: true,
                doubleClick: (e, node) => onNodeSelectionChanged(node)
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
                            new go.Binding("text", "key")
                        ),
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
                
                doubleClick: (e, link) => onLinkSelectionChanged(link),
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
    agentForm.reset();
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

// Function to load diagram data
function loadDiagramData(diagramData, dropdown=true, refresh=true) {
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
    if (dropdown){updateAgentDropdowns();}
    
    if(refresh){
        myDiagram.layoutDiagram(true)
        ensureAllAgentsVisible();
    };
    
}



function DiagramData(){
    const diagramData = {
        nodes: myDiagram.model.nodeDataArray,
        links: myDiagram.model.linkDataArray
    };
    return diagramData
}


function redrawDiagram(dropdown=true, refresh=true) {
    loadDiagramData(DiagramData(),dropdown,refresh);
}

// Function to load diagram from JSON loadJsonFile
function loadDiagramFromDisk(file) {
    const reader = new FileReader();
    reader.onload = function(event) {
        try {
            const diagramData = JSON.parse(event.target.result);
            loadDiagramData(diagramData);
        } catch (error) {
            alert('Error loading diagram: Invalid file format');
            console.error('Error loading diagram:', error);
        }
    };
    reader.readAsText(file);
}

// Function to load diagram from JSON loadDiagramFromServer
function loadDiagramFromServer(fileName) {
    fetch(`/chatapp/designer/json-files/${fileName}`)
        .then(response => response.json())
        .then(diagramData => {
            loadDiagramData(diagramData);
        })
        .catch(error => console.error('Error loading JSON file:', error));
}


// Function to save the current diagram to the server
function saveDiagramToServer() {
    const diagramName = document.getElementById('diagramNameInput').value.trim();
    if (!diagramName) {
        alert('Please enter a name for the diagram.');
        return;
    }
    const diagramData = DiagramData();
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
            diagramFilesPopulate();
        } else {
            alert('Error saving diagram: ' + data.error);
        }
    })
    .catch(error => console.error('Error saving diagram:', error));
}
// Event listener for save button
const saveDiagramToServerBtn = document.getElementById('saveCurrentDiagram');
if (saveDiagramToServerBtn) {
    saveDiagramToServerBtn.addEventListener('click', saveDiagramToServer);
}



// Function to save diagram as JSON
function saveDiagramToDisk() {
    const diagramData = DiagramData();
    
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

const saveDiagramToDiskBtn = document.getElementById('saveButton');
if (saveDiagramToDiskBtn) { 
    saveDiagramToDiskBtn.addEventListener('click', function(e) {
        e.preventDefault();
        saveDiagramToDisk();
    });
}


// Function to populate the explorer with markdown files
function explorerPopulate() {
    fetch('/chatapp/designer/list_markdown_files/')
        .then(response => response.json())
        .then(data => {
            const explorerList = document.getElementById('explorer_analyses');
            explorerList.innerHTML = '';
            data.files.forEach(file => {
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item';
                listItem.style.cursor = 'pointer';
                // Remove .json.md extension from the file name
                const fileName = file.replace(/\.json\.md$/, '');
                listItem.textContent = fileName;
                listItem.linkFile = file;
                listItem.onclick = () => {
                    // Remove the 'active' class from all list items
                    const items = explorerList.querySelectorAll('.list-group-item');
                    items.forEach(item => item.classList.remove('active'));
                    // Add the 'active' class to the clicked item
                    listItem.classList.add('active');
                    

                    const downloadMarkdownBtnTitle = listItem.linkFile;
                    document.getElementById('downloadMarkdownBtnTitle').innerText = downloadMarkdownBtnTitle
                    fetch(`/chatapp/designer/get_markdown_output/?diagramName=${encodeURIComponent(file)}`)
                    .then(response => response.text())
                    .then(markdownContent => {
                        const resultDiv = document.getElementById('crewaiResult');
                        contentMD = JSON.parse(markdownContent)
                        //console.log(contentMD.content);
                        
                        resultDiv.innerHTML = `${marked.parse(contentMD.content)}`;
                        const modal = new bootstrap.Modal(document.getElementById('crewaiModal'));
                        modal.show();
                    })
                    .catch(error => {
                        console.error('Error fetching markdown:', error);
                    });
                    //document.getElementById('diagramNameInput').value = file;
                };
                explorerList.appendChild(listItem);
            });
        })
        .catch(error => console.error('Error fetching markdown files:', error));
}

// Function to fetch JSON files and populate the modal
function diagramFilesPopulate() {
    fetch('/chatapp/designer/json-files') // Assuming a backend endpoint exists
        .then(response => response.json())
        .then(files => {
            const fileList = document.getElementById('jsonFileList');
            fileList.innerHTML = '';
            files.forEach(file => {
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item';
                listItem.style.cursor = 'pointer';
                // Remove .json.md extension from the file name
                const fileName = file.replace(/\.json\.md$/, '');
                listItem.textContent = fileName;
                listItem.ondblclick = () => { 
                    // Remove the 'active' class from all list items
                    const items = fileList.querySelectorAll('.list-group-item');
                    items.forEach(item => item.classList.remove('active'));
                    // Add the 'active' class to the clicked item
                    listItem.classList.add('active');
                    const jsonFilesModalElement = document.getElementById('jsonFilesModal');
                    const jsonFilesModal = bootstrap.Modal.getInstance(jsonFilesModalElement) || new bootstrap.Modal(jsonFilesModalElement);
                    jsonFilesModal.hide();
                    loadDiagramFromServer(file);
                    document.getElementById('diagramNameInput').value = file;
                    
                };
                listItem.onclick = () => {
                    // Remove the 'active' class from all list items
                    const items = fileList.querySelectorAll('.list-group-item');
                    items.forEach(item => item.classList.remove('active'));
                    // Add the 'active' class to the clicked item
                    listItem.classList.add('active');

                    document.getElementById('diagramNameInput').value = file;
                };
                fileList.appendChild(listItem);
            });
        })
        .catch(error => console.error('Error fetching JSON files:', error));
}

// Function to sharepoint files select
function sharepointFilesSelectPopulate() {
    fetch('/chatapp/get_sharepoint_files/')
    .then(response => response.json())
    .then(data => {
        const fileSelect = document.getElementById('agentFile');
        const currentValue = fileSelect.value; // Store current selected value
        fileSelect.innerHTML = '<option value="">Select a file...</option>'; // Clear existing options
        data.files.forEach(file => {
            const option = document.createElement('option');
            option.value = file.path;
            option.textContent = `${file.analyse} / ${file.name}`;
            fileSelect.appendChild(option);
        });
        // Reapply the selection if it exists
        if (currentValue) {
            fileSelect.value = currentValue;
        }
    })
    .catch(error => console.error('Error loading files:', error));
}

// Attach event listener to modal show event
const jsonFilesModal = document.getElementById('jsonFilesModal');
if (jsonFilesModal) {
    jsonFilesModal.addEventListener('show.bs.modal', diagramFilesPopulate);
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
            diagramFilesPopulate(); // Refresh the list
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
agentForm.addEventListener("submit", function(e) {
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
    // resetAgentForm();
    // xuxa to delete
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

// Function to delete markdown file
function deleteMarkdownFile(filename) {
    fetch('/chatapp/designer/delete-markdown-file/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ filename: filename })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            explorerPopulate()
            //alert('File deleted successfully.');
            $('#crewaiModal').modal('hide');
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while deleting the file.');
    });
}

// Initialize diagram when page loads
window.onload = function() {
    init();
    diagramFilesPopulate();
    explorerPopulate() 
    sharepointFilesSelectPopulate()

    // Add save button handler
    
    
    // Add load button handler
    document.getElementById('loadButton').addEventListener('change', function(e) {
        if (this.files && this.files[0]) {
            if (confirm('Loading a new diagram will replace the current one. Are you sure you want to continue?')) {
                loadDiagramFromDisk(this.files[0]);
            }
            this.value = ''; // Reset file input
        }
    });
    
    // Add delete markdown button handler
    document.getElementById('deleteMarkdownBtn').addEventListener('click', function() {
        const filename = document.getElementById('downloadMarkdownBtnTitle').textContent.trim();
        // alert(filename)
        
        if (!filename) {
            alert('No file specified to delete.');
            return;
        }

        deleteMarkdownFile(filename)
    });



    // Add event listener for agentModalBtn
    document.getElementById('agentModalBtn').addEventListener('click', function() {
        var agentModal = new bootstrap.Modal(document.getElementById('agentModal'));
        agentModal.show();
        resetAgentForm();
    });

    // Add event listener for taskModalBtn
    document.getElementById('taskModalBtn').addEventListener('click', function() {
        var taskModal = new bootstrap.Modal(document.getElementById('taskModal'));
        taskModal.show();
        resetRelationshipForm();
    });

    // Add event listener for agentModal
    document.getElementById('agentModal').addEventListener('show.bs.modal', function() {
        sharepointFilesSelectPopulate();
    });

    // Add refresh layout button handler
    document.getElementById('refreshLayoutBtn').addEventListener('click', function() {
        redrawDiagram()
        myDiagram.layoutDiagram(true);
        ensureAllAgentsVisible();
    });


    // Add create CrewAI button handler
    document.getElementById('createCrewAIBtn').addEventListener('click', function() {
        // Get the diagram data
        const diagramData = {
            nodes: myDiagram.model.nodeDataArray,
            links: myDiagram.model.linkDataArray
        };

        // Add diagramNameInput to the diagram data
        const diagramNameInput = document.getElementById('diagramNameInput').value;
        diagramData.diagramNameInput = diagramNameInput;

        // Send to backend
        fetch('/chatapp/designer/launch_crewai/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(diagramData)
        })
        .then(response => response.json())
        .then(data => {
            // Display result in modal
            const resultDiv = document.getElementById('crewaiResult');
            if (data.status === 'success') {
                // Convert markdown message to HTML
                const messageHtml = marked.parse(data.message);
                
                resultDiv.innerHTML = `<div class="text-success mb-3">Process completed successfully!</div>
                                     <div class="markdown-body">${messageHtml}</div>
                                     <div class="mt-3">
                                         <strong>Agents:</strong> ${data.agents_count}<br>
                                         <strong>Tasks:</strong> ${data.tasks_count}
                                     </div>`;
            } else {
                resultDiv.innerHTML = `<div class="text-danger mb-3">Error occurred during process</div>
                                     <div>${data.message}</div>`;
            }

            // Show the modal
            const modal = new bootstrap.Modal(document.getElementById('crewaiModal'));
            explorerPopulate()
            modal.show();
        })
        .catch(error => {
            console.error('Error:', error);
            const resultDiv = document.getElementById('crewaiResult');
            resultDiv.innerHTML = `<div class="text-danger mb-3">Error occurred during process</div>
                                 <div>Error creating CrewAI process: ${error.message}</div>`;
            const modal = new bootstrap.Modal(document.getElementById('crewaiModal'));
            modal.show();
        });
    });

    

    document.getElementById('downloadMarkdownBtn').addEventListener('click', function() {
        const diagramNameInput = document.getElementById('downloadMarkdownBtnTitle').innerText;
    
        fetch(`/chatapp/designer/get_markdown_output/?diagramName=${encodeURIComponent(diagramNameInput)}`)
            .then(response => response.json())
            .then(data => {
                if (data.content) {
                    const blob = new Blob([data.content], { type: 'text/markdown' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `${diagramNameInput}.md`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                } else {
                    console.error('Error: File content not found');
                }
            })
            .catch(error => {
                console.error('Error fetching markdown:', error);
            });
    });

};

// Helper function to get CSRF token
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

/* General function to open a tab (ie. hide evrything except for the div with id `contentID` that belongs to this `contentClass`)

For example, if we have 2 divs
<div class="dogsContent" id="beagleDiv"> ... </div>
<div class="dogsContent" id="goldenRetrieverDiv"> ... </div>
then calling openTab('dogsContent', 'beagleDiv') will show only the content from the first div.

Other divs are not affected.
*/
function openTab(contentClass, contentId) {
    for (var content of document.getElementsByClassName(contentClass)) {
        content.style.display = "none";
    }
    document.getElementById(contentId).style.display = "block";
}

/* Returns the length of the box that holds all the collection cards in the current viewport width. */
function getLengthCardContainer(){
    for (var content of document.getElementsByClassName("cardcontainer")) {
        // only the parent element (the main div that is directly linked to the tabs) has it's style.display set to none
        if (content.parentElement.style.display !== "none") return content.offsetWidth;
    }
}

/* This function is to try to make every shown collection cards look sufficiently similar (no glaring styling differences.)
Does these things:
1. Try to fill up as much space as possible lengthwise, while ensuring the card length is around `cardLength` (maximum deviation of 1/2 * `cardLength`)
2. Standarise the height of the card's title and description box to the maximum of all shown cards
3. Standarise the height of the whole collection card to be the maximum of the height of all cards, or 200px (as per style rule)
*/

function normaliseCard(cardLength){
    var containerLen = getLengthCardContainer();
    // for this length of card container, how many cards are we expecting to fit, if each card width is around the length of 'cardLength'?
    var expectedCards = Math.round(containerLen / cardLength);
    var maxHeight = 0;
    var maxTitleHeight = 0;
    var maxDescHeight = 0;
    for (var content of document.getElementsByClassName("collectionCard")) {
        // div [class='collectionscontainer'] -> div[class='flex-container'] -> div[class='collectionCardBorder'] -> div [class='collectionCard']
        if (content.parentElement.parentElement.parentElement.style.display === 'none') continue; // do not EVER touch display:none elements
        content.style.width = (containerLen / expectedCards) - 30 + "px"; // 30px offset because of margin
        // calculate max height of the whole card for all cards
        maxHeight = Math.max(content.offsetHeight, maxHeight);

        // calculate max height of the title text for all cards
        var title = content.getElementsByClassName("card-header");
        if (title.length !== 0){
            var actualTitleHeight = title[0].getElementsByClassName("card-title")[0].offsetHeight;
            maxTitleHeight = Math.max(actualTitleHeight, maxTitleHeight);
        }

        // calculate max height of the description div (that contains the short description of the collection) for all cards
        var desc = content.getElementsByClassName("card-desc")
        if (desc.length !== 0){
            var actualDescHeight = desc[0].offsetHeight;
            maxDescHeight = Math.max(actualDescHeight, maxDescHeight);
        }
    }
    for (var content of document.getElementsByClassName("collectionCard")) {
        if (content.parentElement.parentElement.parentElement.style.display === 'none') continue;
        content.style.height = maxHeight + "px";
        var title = content.getElementsByClassName("card-header");
        if (title.length !== 0){
            title[0].style.height = maxTitleHeight + "px";
        }
        var desc = content.getElementsByClassName("card-desc");
        if (desc.length !== 0){
            desc[0].style.height = maxDescHeight + "px";
        }
    }
}
// used to detect <idName><num> so that we can increase num by 1 for every new element.
// after calling .match(), it will return [<fullMatch>, <namePortion>, <endNumber>]
const idRegex = /^(.*?)(\d+)$/i; 

/* Get the smallest number x, such that adding a new row with id "<standarised id for `clonedInputElems`>" + str(1...Infinity)
   will not cause an ID clash. 

   Assumptions:
   1. All IDs of elements in clonedInputElements are of the following format: "<some constant string><num>"
   2. The very last element of `clonedInputElems` has such x.
*/
function getLargestProblemIndex(clonedInputElems){
    var latestElem = clonedInputElems[clonedInputElems.length-1];
    var matching = latestElem.id.match(idRegex);
    return parseInt(matching[2]);
}

/* Get the total number of problems in the form in the modal.
   Assumptions:
   1. The document tree is as follows:
      <... id="`modalID`">
        <div>
            <div>
                <form>
                    <table>
                        <tbody>
                            <... class="clonedInput">
   2. All rows that signify a problem has the class clonedInput.
*/
function getNumProblems(modalId){
    var elems = document.querySelectorAll("#" + modalId + " div div form table tbody .clonedInput");
    return elems.length;
}

/* Disables all buttons in `removeButtonsElems` if currLength is exactly 1, or else enable them back.

   Used for ensuring that the user does not delete all the rows such that they cannot be cloned back if they need
   to add more problems later on.
*/
function toggleDelete(removeButtonElems, currLength){
    for (var elem of removeButtonElems){
        elem.disabled = (currLength == 1);
    }
}

/* Opens the modal `modalId`.

   The parameter `problemLengthCanChange` is used to signify whether the collection form allows users to add more problems.
   If true, we initialise the special 'functions' for this form
*/
function openModal(modalId, problemLengthCanChange=false){
    document.getElementById(modalId).style.display='block';
    if (problemLengthCanChange){
        var currProblemLength = getNumProblems(modalId);
        var removeButtons = document.querySelectorAll("#" + modalId + " div div form table tbody .clonedInput td .remove");
        toggleDelete(removeButtons, currProblemLength);
    }
}

/* Closes the modal with id modalId.
   Always use this function before opening any other modals.
 */
function closeModal(modalId){
    document.getElementById(modalId).style.display='none';
}

/* Clone the input row the pressed button is at. */
function clone(){
    var idx = getLargestProblemIndex(this.closest(".clonedInput").parentElement.querySelectorAll(".clonedInput")) + 1;
    var sampleRow = this.closest(".clonedInput");
    var clonedElement = sampleRow.cloneNode(true);
    var namePart = clonedElement.id.match(idRegex)[1];
    clonedElement.id = namePart + idx;
    for (var container of clonedElement.childNodes){
        if (container.tagName == "TD"){
            for (var elem of container.childNodes){
                /* just in case the elem has no id or name, the program would not set an invalid one */
                var elemID = elem.id || '';
                var matches = elemID.match(idRegex)
                if (matches !== null && matches.length == 3){
                    elem.id = matches[1] + idx;
                }
                var elemName = elem.name || '';
                matches = elemName.match(idRegex);
                if (matches !== null && matches.length == 3){
                    elem.name = matches[1] + idx;
                }
            }
        }
    }
    sampleRow.parentElement.appendChild(clonedElement);
    document.querySelector("#" + clonedElement.id + " td .clone").onclick = clone;
    document.querySelector("#" + clonedElement.id + " td .remove").onclick = remove;
    toggleDelete(sampleRow.parentElement.querySelectorAll(".clonedInput td .remove"), getNumProblems(this.closest(".w3-modal").id));
}

/* Remove the row the pressed remove button is at */
function remove(){
    var currProblemLength = getNumProblems(this.closest(".w3-modal").id);
    var toDeleteRow = this.closest(".clonedInput");
    var allRowContainer = toDeleteRow.parentElement;
    toDeleteRow.remove();
    currProblemLength -= 1;
    var deleteButtons = allRowContainer.querySelectorAll(".clonedInput td .remove");
    toggleDelete(deleteButtons, currProblemLength);
}

/* These functions allow the user to reorder the problems in "Edit / Add Collections Mode by dragging them. */
var currDraggedRow;
function start(){
    currDraggedRow = event.target;
}

function dragover(){
    var e = event;
    e.preventDefault();
    var currTableBody = e.target.parentElement.parentElement;
    if (currTableBody.nodeName !== "TBODY"){
        // something is wrong, we DO NOT change any element
        return;
    }
    var currProblems = Array.from(currTableBody.children);
    try{
        if(currProblems.indexOf(e.target.parentElement) > currProblems.indexOf(currDraggedRow)){
            e.target.parentElement.after(currDraggedRow);
        } else {
            e.target.parentElement.before(currDraggedRow);
        }
    } catch (error){
        if (error instanceof DOMException){
            // when dragover, we drag over the current dragged element.
            // we just silence the error
        } else {
            // oops something really went wrong.
            throw error;
        }
    }
}

/* Modify the IDs of the form such that they are in increasing order again. */
function reorder(){
    var currProblems = event.target.parentElement.children;
    var sampleTRID = currProblems[0].id;
    var baseName = sampleTRID.match(idRegex)[1];
    for (var i = 0; i < currProblems.length; i++){
        currProblems[i].id = baseName + i;
        for (var elemTD of currProblems[i].children){
            for (var inputElem of elemTD.children){
                /* just in case the elem has no id or name, the program would not set an invalid one */
                var elemID = inputElem.id || ''; 
                var matches = elemID.match(idRegex)
                if (matches !== null && matches.length == 3){
                    inputElem.id = matches[1] + i;
                }
                var elemName = inputElem.name || '';
                matches = elemName.match(idRegex);
                if (matches !== null && matches.length == 3){
                    inputElem.name = matches[1] + i;
                }
            }
        }
    }
}

/* Resets the "Delete Collections" 'form' by unchecking all the checkboxes.

   Used after the current tab is changed or the user cancels the "Delete Collections" operation so that collections do not get deleted on accident.
*/
function clearAllDeleteCheckboxes(){
    for (var elem of document.getElementsByClassName('deleteCollectionCheckboxSpan')){
        elem.getElementsByTagName("input")[0].checked = false;
        elem.style.display = "none";
    }
}

/* Enables "Delete Collection" mode in this tab. The user can now check the collections that they want to delete, and click "Delete" to delete all of them. */
function openDeleteCollectionsForm(tabContentID){
    var currentTab = document.getElementById(tabContentID);
    var cancelButton = document.getElementById('cancelbutton');
    cancelButton.style.display = "inline-block";
    cancelButton.onclick = function(){
        clearAllDeleteCheckboxes();
        this.style.display = "none";
        document.getElementById("deletebutton").style.display = "none";
        document.getElementById("editcollectionsbutton").style.display = "inline-block";
    }
    document.getElementById("deletebutton").style.display = "inline-block";
    for (var elem of currentTab.getElementsByClassName("deleteCollectionCheckboxSpan")){
        elem.style.display = "block";
    }
}

/* The more specialised version of openTab(). Also has a parameter 'canEdit' which signals if the collections there can be edited (deleted). */
function openCollectionsTab(tabContentID, canEdit){
    openTab("collectionscontainer", tabContentID);
    normaliseCard(cardLength);
    if (canEdit){
        var editCollectionButton = document.getElementById("editcollectionsbutton");
        editCollectionButton.style.display = "inline-block";
        editCollectionButton.onclick = function(){
            // ensures that only those checkboxes relevant are shown, the other irrelevant checkboxes are still hidden 
            // (if we ever want to add another editable collection tab)
            clearAllDeleteCheckboxes();
            this.style.display = "none";
            openDeleteCollectionsForm(tabContentID);
        }
    } else {
        // always help reset state to original properly
        clearAllDeleteCheckboxes();
        document.getElementById("editcollectionsbutton").style.display = "none";
        document.getElementById("deletebutton").style.display = "none";
        document.getElementById("cancelbutton").style.display = "none";
    }
}

/* The TODO table and the other problems table has the same problems row, but only those relevant are shown.
To "move" from TODO table to other problem or vice versa, we just need to swap the visibility of these rows.
*/
function swapTODOAndOthers(rowClass){
    for (var elem of document.getElementsByClassName(rowClass)){
        if (elem.classList.length == 2) elem.classList.remove("invisibleAfterLoad")
        else elem.classList.add("invisibleAfterLoad");
    }
}

const trRegex = /^(.*?)Tr(\d+)$/i; // detects <idName>Tr<num>

/* Change the importance of the current problem.
   if importance is "True", we move the current problem to the TODO list.
   if importance is "False", we move the current problem out of the TODO list.

   Assumes that there will be a change after this operation.
*/
function changeImportance(currProblem, importance){
    var rowClass = currProblem.classList[0];
    swapTODOAndOthers(rowClass);
    var matches = rowClass.match(trRegex);
    // id of hidden form to update importance is <idName>isImportant<num>
    var idImportance = matches[1] + "isImportant" + matches[2];
    document.getElementById(idImportance).value = importance; 
}

function addToTODO(){
    changeImportance(this.parentElement.parentElement, "True"); // tree is from td -> tr -> button
}

function removeFromTODO(){
    changeImportance(this.parentElement.parentElement, "False"); // tree is from td -> tr -> button
}

/* Updates all input fields with class `className` to `value`. Does not check if it is valid or sound. */
function updateAll(className, value){
    for (var elem of document.getElementsByClassName(className)){
        elem.value = value;
    }
}

const cardLength = 360;
window.onload = function(){
    openCollectionsTab("publicCollectionsDiv");
    for (var elem of document.getElementsByClassName("clone")){
        elem.onclick = clone;
    }
    for (var elem of document.getElementsByClassName("remove")){
        elem.onclick = remove;
    }
    for (var elem of document.getElementsByClassName("addToTODO")){
        elem.onclick = addToTODO;
    }
    for (var elem of document.getElementsByClassName("removeFromTODO")){
        elem.onclick = removeFromTODO;
    }
}

window.onresize = function(){
    normaliseCard(cardLength);
}
function openTab(contentClass, contentId) {
    for (var content of document.getElementsByClassName(contentClass)) {
        content.style.display = "none";
    }
    document.getElementById(contentId).style.display = "block";
}

function getLengthCardContainer(){
    for (var content of document.getElementsByClassName("cardcontainer")) {
        if (content.style.display !== "none") return content.offsetWidth;
    }
}

function normaliseCardLength(cardLength){
    var containerLen = getLengthCardContainer();
    var expectedCards = Math.round(containerLen / cardLength);
    var maxHeight = 0;
    var maxTitleHeight = 0;
    var maxDescHeight = 0;
    for (var content of document.getElementsByClassName("collectionCard")) {
        if (content.parentElement.parentElement.style.display === 'none') continue;
        content.style.width = (containerLen / expectedCards) - 30 + "px"; // 30px offset because of margin
        maxHeight = Math.max(content.offsetHeight, maxHeight);
        var title = content.getElementsByClassName("card-header");
        if (title.length !== 0){
            var actualTitleHeight = title[0].getElementsByClassName("card-title")[0].offsetHeight;
            maxTitleHeight = Math.max(actualTitleHeight, maxTitleHeight);
        }
        var desc = content.getElementsByClassName("card-desc")
        if (desc.length !== 0){
            var actualDescHeight = desc[0].offsetHeight;
            maxDescHeight = Math.max(actualDescHeight, maxDescHeight);
        }
    }
    for (var content of document.getElementsByClassName("collectionCard")) {
        if (content.parentElement.parentElement.style.display === 'none') continue;
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
var idx = 0;
const idRegex = /^(.*?)(\d+)$/i; // used to detect <idName><num> so that we can increase num by 1 for every new element.

function getLargestProblemIndex(modalId){
    var elems = document.querySelectorAll("#" + modalId + " div div form table tbody .clonedInput");
    var latestElem = elems[elems.length-1];
    var matching = latestElem.id.match(idRegex);
    return parseInt(matching[2]);
}

function getNumProblems(modalId){
    var elems = document.querySelectorAll("#" + modalId + " div div form table tbody .clonedInput");
    return elems.length;
}

function toggleDelete(removeButtonElems, currLength){
    for (var elem of removeButtonElems){
        elem.disabled = (currLength == 1);
    }
}

function openModal(modalId){
    document.getElementById(modalId).style.display='block';
    idx = getLargestProblemIndex(modalId);
    var currProblemLength = getNumProblems(modalId);
    var removeButtons = document.querySelectorAll("#" + modalId + " div div form table tbody .clonedInput td .remove");
    toggleDelete(removeButtons, currProblemLength);
}

function closeModal(modalId){
    document.getElementById(modalId).style.display='none';
}

function openCollectionsTab(tabID){
    openTab("collectionscontainer", tabID);
    normaliseCardLength(cardLength);
}

function clone(){
    idx += 1;
    var sampleRow = this.closest(".clonedInput");
    var clonedElement = sampleRow.cloneNode(true);
    clonedElement.id = "clonedInput" + idx;
    for (var container of clonedElement.childNodes){
        if (container.tagName == "TD"){
            for (var elem of container.childNodes){
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
    console.log(sampleRow.parentElement.querySelectorAll(".clonedInput td .remove"));
    toggleDelete(sampleRow.parentElement.querySelectorAll(".clonedInput td .remove"), getNumProblems(this.closest(".w3-modal").id));
}

function remove(){
    var currProblemLength = getNumProblems(this.closest(".w3-modal").id);
    var toDeleteRow = this.closest(".clonedInput");
    var allRowContainer = toDeleteRow.parentElement;
    toDeleteRow.remove();
    currProblemLength -= 1;
    var deleteButtons = allRowContainer.querySelectorAll(".clonedInput td .remove");
    toggleDelete(deleteButtons, currProblemLength);
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

function addToTODO(){
    var currRow = this.parentElement.parentElement; // tree is from td -> tr -> button
    var rowClass = currRow.classList[0];
    swapTODOAndOthers(rowClass);
    var matches = rowClass.match(trRegex);
    // id of hidden form to update importance is <idName>isImportant<num>
    var idImportance = matches[1] + "isImportant" + matches[2];
    console.log(idImportance);
    document.getElementById(idImportance).value = "True"; 
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
}

window.onresize = function(){
    normaliseCardLength(cardLength);
}
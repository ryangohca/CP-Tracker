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
    for (var content of document.getElementsByClassName("collectionCard")) {
        if (content.parentElement.parentElement.style.display === 'none') continue;
        content.style.width = (containerLen / expectedCards) - 30 + "px"; // 30px offset because of margin
        maxHeight = Math.max(content.offsetHeight, maxHeight);
    }
    for (var content of document.getElementsByClassName("collectionCard")) {
        if (content.parentElement.parentElement.style.display === 'none') continue;
        content.style.height = maxHeight + "px"; // 30px offset because of margin
    }
}
var idx = 0;
var idRegex = /^(.*)(\d)+$/i;

function getLargestProblemIndex(modalId){
    var elems = document.querySelectorAll("#" + modalId + " div div form table tbody .clonedInput");
    var latestElem = elems[elems.length-1];
    var matching = latestElem.id.match(idRegex);
    return parseInt(matching[2]);
}

function openModal(modalId){
    document.getElementById(modalId).style.display='block';
    idx = getLargestProblemIndex(modalId);
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
    var clonedElement = this.closest(".clonedInput").cloneNode(true);
    clonedElement.id = "clonedInput" + idx;
    for (var elem of clonedElement.childNodes){
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
    this.closest(".clonedInput").parentElement.appendChild(clonedElement);
    document.querySelector("#" + clonedElement.id + " td .clone").onclick = clone;
    document.querySelector("#" + clonedElement.id + " td .remove").onclick = remove;
}

function remove(){
    // do nothing for now
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
}

window.onresize = function(){
    normaliseCardLength(cardLength);
}
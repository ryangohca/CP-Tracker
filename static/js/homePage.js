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

function openModal(modalId){
    document.getElementById(modalId).style.display='block';
}

function closeModal(modalId){
    document.getElementById(modalId).style.display='none';
}

function openCollectionsTab(tabID){
    openTab("collectionscontainer", tabID);
    normaliseCardLength(cardLength);
}
const cardLength = 360;
window.onload = function(){
    openCollectionsTab("publicCollectionsDiv");
}

window.onresize = function(){
    normaliseCardLength(cardLength);
}
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
        content.style.width = (containerLen / expectedCards) - 30 + "px"; // 30px offset because of margin
        maxHeight = Math.max(content.offsetHeight, maxHeight);
    }
    for (var content of document.getElementsByClassName("collectionCard")) {
        content.style.height = maxHeight + "px"; // 30px offset because of margin
    }
}

const cardLength = 360;
window.onload = function(){
    openTab("collectionscontainer", "publicCollectionsDiv");
    normaliseCardLength(cardLength);
};

window.onresize = function(){
    normaliseCardLength(cardLength);
}
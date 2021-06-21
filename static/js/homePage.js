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
    console.log(containerLen);
    var expectedCards = Math.floor(containerLen / cardLength);
    for (var content of document.getElementsByClassName("collectionCard")) {
        content.style.width = (containerLen / expectedCards) - 30 + "px"; // 30px offset because of margin
    }
}

window.onload = function(){
    openTab("collectionscontainer", "publicCollectionsDiv");
    normaliseCardLength(350);
};

window.onresize = function(){
    normaliseCardLength(350);
}
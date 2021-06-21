function openTab(contentClass, contentId) {
    for (var content of document.getElementsByClassName(contentClass)) {
        content.style.display = "none";
    }
    document.getElementById(contentId).style.display = "block";
}

window.onload = function(){
    openTab("collectionscontainer", "publicCollectionsDiv");
};
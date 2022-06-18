function deleteNote(productID) {
    fetch("/delete_product",{
        method : "POST",
        body: JSON.stringify({productID: productID})
    }).then((_res) => {
        window.location.href = "/admin";
    });
}

function editNote(productID) {
    window.location.href = "/admin/edit_product/"+productID;
}

function deleteCategory(categoryID) {
    fetch("/delete_category",{
        method : "POST",
        body: JSON.stringify({categoryID: categoryID})
    }).then((_res) => {
        window.location.href = "/admin/add_category";
    });
}

function removeFromCart(categoryID) {
    fetch("/remove_from_cart",{
        method : "POST",
        body: JSON.stringify({categoryID: categoryID})
    }).then((_res) => {
        window.location.href = "/cart";
    });
}

function editCart(productID) {
    window.location.href = "/edit_cart/"+productID;
}


function submitValue(productID) {
    window.location.href = "/submitValue/"+productID;
    
}


document.getElementById('yourBox').onchange = function() {
    document.getElementById('yourText').disabled = !this.checked;
};
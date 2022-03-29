const navList = document.querySelector('.nav-ul');
const burger = document.querySelector('.nav-burger');

// toggle Mobile burger menu on/off
function toggleBurger() {
    // burger menu is open, so close it
    if (navList.classList.contains('active')) {
        navList.classList.remove('active');
        // replace "X" symbol with burger icon
        burger.querySelector('a').innerHTML = "<i class='fas fa-bars'></i>";
    }
    else {
        navList.classList.add('active');
        // replace burger icon with "X" symbol
        burger.querySelector('a').innerHTML = "<i class='fas fa-times'></i>";
    }
}

burger.addEventListener('click', toggleBurger);

// close burger menu if open by clicking anywhere on page
function closeBurger() {
    if (navList.classList.contains('active')) {
        navList.classList.remove('active');
        // replace "X" symbol with burger icon
        burger.querySelector('a').innerHTML = "<i class='fas fa-bars'></i>";
    }
}

const pageBody = document.querySelector('main');
pageBody.addEventListener('click', closeBurger);
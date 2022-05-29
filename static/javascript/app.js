// Swiper library used for carousel
var swiper = new Swiper(".mySwiper", {
        slidesPerView: "auto",
        spaceBetween: 30,
        freeMode: true,
      });

// Makes sure that the submit button is disabled till there is input
var element = document.querySelector("#search-input");
var button = document.querySelector("#btn");
var sb = document.getElementById("box");
button.disabled = true;
function myScript(){
    txt = element.value;
    if (txt==""){
        button.disabled = true;
        sb.classList.remove('search-box-active');
    }
    else{
        button.disabled = false;
        sb.classList.add('search-box-active');
    }
}
element.addEventListener("input", myScript);
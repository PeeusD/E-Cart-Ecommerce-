$('#slider1, #slider2, #slider3').owlCarousel({
    loop: true,
    margin: 20,
    responsiveClass: true,
    responsive: {
        0: {
            items: 1,
            nav: false,
            autoplay: true,
        },
        600: {
            items: 3,
            nav: true,
            autoplay: true,
        },
        1000: {
            items: 5,
            nav: true,
            loop: true,
            autoplay: true,
        }
    }
})

$('.plus-cart').click(function(){
    let id = $(this).attr("pid").toString();
    let elm = this.parentNode.children[2]
    // console.log(elm)
    $.ajax({
        type:"GET",
        url:"/quantity_cart",
        data: {
            prod_plus_id:id
        },
        success: function(data){
            // console.log(data)
            elm.innerText = data.quantity
            document.getElementById("amount").innerText = data.amount
            document.getElementById("totalamount").innerText = data.totalamount
        }
    })
})


$('.minus-cart').click(function(){
    let id = $(this).attr("pid").toString();
    let elm = this.parentNode.children[2]
    // console.log(elm)
    $.ajax({
        type:"GET",
        url:"/quantity_cart",
        data: {
            prod_minus_id:id
        },
        success: function(data){
            // console.log(data)
            elm.innerText = data.quantity
            document.getElementById("amount").innerText = data.amount
            document.getElementById("totalamount").innerText = data.totalamount
        }
    })
})


$('.remove-cart').click(function(){
    let id = $(this).attr("pid").toString();
    let elm = this
    // console.log(elm)
    $.ajax({
        type:"GET",
        url:"/remove_cart",
        data: {
            prod_remove_id:id
        },
        success: function(data){
            // console.log(data)
        
            document.getElementById("amount").innerText = data.amount
            document.getElementById("totalamount").innerText = data.totalamount
            elm.parentNode.parentNode.parentNode.parentNode.remove()
        }
    })
})



//paynow ajax request with passing custidvalue by checked radio button

$('#pay-now').click(function(){
    let custid = $('input[name="custid"]:checked').attr("value");
    // console.log(custid);
    $.ajax({
        type:"GET",
        url:"/paymentdone/",
        data: {
           custid:custid
        },
        success: function(data){
            //modal script
            $("#confirm-payment").attr("href", data.payment_url);
            var myModal = document.getElementById('confirmModal')
            var myInput = document.getElementById('myInput')
            
            myModal.addEventListener('shown.bs.modal', function () {
            myInput.focus()
            })

            
        
            
        }
    })
 
      });


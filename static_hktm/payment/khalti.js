

function khalti_payment(product_name,product_sku, product_url,total_amount,csrf_token,public_key){

// var getUrl = window.location;
// var baseUrl = getUrl.protocol + "//" + getUrl.host + "";
productName = product_name;
productSku = product_sku;
productUrl = product_url;



var config = {
    // replace the publicKey with yours
    "publicKey": public_key,
    "productIdentity": productSku,
    "productName": productName,
    "productUrl": productUrl,
    "eventHandler": {
        onSuccess(payload) {
            run(payload,csrf_token);
        },
        onError(error) {
        },
        onClose() {
        }
    }
};

var checkout = new KhaltiCheckout(config);
var btn = document.getElementById("khalti-payment");
btn.onclick = function () {
    var amount = total_amount;
    //var amount = {{ grand_total}};
    checkout.show({amount: amount * 100});
}
}


function run(payload,token) {
    var getUrl = window.location;
    var baseUrl = getUrl.protocol + "//" + getUrl.host + "";

    $.ajax({
        type: 'POST',
        url: `${baseUrl}/payment/khalti`,
        data: {
            'token': payload.token,
            'amount': payload.amount,
            'csrfmiddlewaretoken': token

        },
        dataType: 'json',

        success: function (json) {

            if (json['status'] === 200) {
                window.location.replace(`${baseUrl}/order/${json['order']}`);
            }
        },
        error: function (xhr, errmsg, err) {
            console.log("hey there", xhr.status,errmsg,err);
        }
    });


}

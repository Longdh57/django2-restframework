var image_outside = new FileReader();
var image_inside = new FileReader();
var image_store_cashier = new FileReader();
var cessation_of_business_image = new FileReader();
var filterType = /^(?:image\/bmp|image\/cis\-cod|image\/gif|image\/ief|image\/jpeg|image\/jpeg|image\/jpeg|image\/pipeg|image\/png|image\/svg\+xml|image\/tiff|image\/x\-cmu\-raster|image\/x\-cmx|image\/x\-icon|image\/x\-portable\-anymap|image\/x\-portable\-bitmap|image\/x\-portable\-graymap|image\/x\-portable\-pixmap|image\/x\-rgb|image\/x\-xbitmap|image\/x\-xpixmap|image\/x\-xwindowdump)$/i;

var loadImageFile = function (id) {
  console.log(id);

  var uploadImage = document.getElementById(id);

  //check and retuns the length of uploded file.
  if (uploadImage.files.length === 0) {
    return;
  }

  //Is Used for validate a valid file.
  var uploadFile = document.getElementById(id).files[0];
  if (!filterType.test(uploadFile.type)) {
    alert("Please select a valid image.");
    return;
  }
  if (id == 'image_outside') {
    image_outside.readAsDataURL(uploadFile);
  } else if (id == 'image_inside') {
    image_inside.readAsDataURL(uploadFile);
  } else if (id == 'image_store_cashier') {
    image_store_cashier.readAsDataURL(uploadFile);
  } else if (id == 'cessation_of_business_image') {
    cessation_of_business_image.readAsDataURL(uploadFile);
  }
};

image_outside.onload = function (event) {
  var image = new Image();

  image.onload = function () {
    var canvas = document.createElement("canvas");
    var context = canvas.getContext("2d");
    canvas.width = image.width / 6;
    canvas.height = image.height / 6;
    context.drawImage(image,
      0,
      0,
      image.width,
      image.height,
      0,
      0,
      canvas.width,
      canvas.height
    );

    document.getElementById("image-outside-upload").src = canvas.toDataURL();
  };
  image.src = event.target.result;
};

image_inside.onload = function (event) {
  var image = new Image();

  image.onload = function () {
    var canvas = document.createElement("canvas");
    var context = canvas.getContext("2d");
    canvas.width = image.width / 6;
    canvas.height = image.height / 6;
    context.drawImage(image,
      0,
      0,
      image.width,
      image.height,
      0,
      0,
      canvas.width,
      canvas.height
    );

    document.getElementById("image-inside-upload").src = canvas.toDataURL();
  };
  image.src = event.target.result;
};

image_store_cashier.onload = function (event) {
  var image = new Image();

  image.onload = function () {
    var canvas = document.createElement("canvas");
    var context = canvas.getContext("2d");
    canvas.width = image.width / 6;
    canvas.height = image.height / 6;
    context.drawImage(image,
      0,
      0,
      image.width,
      image.height,
      0,
      0,
      canvas.width,
      canvas.height
    );

    document.getElementById("image-store-cashier-upload").src = canvas.toDataURL();
  };
  image.src = event.target.result;
};

cessation_of_business_image.onload = function (event) {
  var image = new Image();

  image.onload = function () {
    var canvas = document.createElement("canvas");
    var context = canvas.getContext("2d");
    canvas.width = image.width / 6;
    canvas.height = image.height / 6;
    context.drawImage(image,
      0,
      0,
      image.width,
      image.height,
      0,
      0,
      canvas.width,
      canvas.height
    );

    document.getElementById("cessation-of-business-image-upload").src = canvas.toDataURL();
  };
  image.src = event.target.result;
};

function dataURItoBlob(dataURI) {
  var byteString = atob(dataURI.split(',')[1]);

  var mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];

  var ab = new ArrayBuffer(byteString.length);
  var ia = new Uint8Array(ab);
  for (var i = 0; i < byteString.length; i++) {
    ia[i] = byteString.charCodeAt(i);
  }
  return new Blob([ia], { "type": mimeString });
};
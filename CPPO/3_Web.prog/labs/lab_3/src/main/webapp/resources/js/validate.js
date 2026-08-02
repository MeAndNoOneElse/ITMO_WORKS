function filterDecimalInput(evt) {
    let v = evt.target.value;
    v = v.replace(/[^0-9.,-]/g, '');
    v = v.replace(/[,]/g, '.');
    if (v.length > 10) v = v.substring(0, 10);
    evt.target.value = v;
}

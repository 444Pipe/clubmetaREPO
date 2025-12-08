(function(){
  function normalizePriceInput(val){
    if(!val) return '';
    var v = String(val).trim();
    v = v.replace(/\s+/g,'');

    // Allow shorthand like 3k or 2.5k or 1m (k = miles, m = millones)
    var shorthand = v.match(/^([0-9.,]+)\s*([kKmM])?$/);
    if (shorthand){
      var num = shorthand[1];
      var suf = shorthand[2];

      // If both separators present, treat as European style (dots thousands, comma decimal)
      if (num.indexOf('.')>-1 && num.indexOf(',')>-1){
        num = num.replace(/\./g,'').replace(',', '.');
      } else if (num.indexOf(',')>-1 && num.indexOf('.')===-1){
        // only commas present: decide if decimal (1-2 digits after last comma) or thousands (3 digits)
        var afterComma = num.substring(num.lastIndexOf(',')+1);
        if (/^\d{1,2}$/.test(afterComma)){
          num = num.replace(/,/g, '.');
        } else {
          // treat commas as thousands separators -> remove them
          num = num.replace(/,/g, '');
        }
      } else if (num.indexOf('.')>-1 && num.indexOf(',')===-1){
        // only dots present: decide if decimal (1-2 digits after last dot) or thousands
        var afterDot = num.substring(num.lastIndexOf('.')+1);
        if (/^\d{1,2}$/.test(afterDot)){
          // keep dot as decimal separator
        } else {
          // remove dots (thousands separators)
          num = num.replace(/\./g,'');
        }
      }

      var parsed = parseFloat(num);
      if (isNaN(parsed)) return '';
      var multiplier = 1;
      if (suf){
        if (suf.toLowerCase() === 'k') multiplier = 1000;
        if (suf.toLowerCase() === 'm') multiplier = 1000000;
      }
      var result = parsed * multiplier;
      // ensure dot decimal for normalization
      return String(result);
    }

    // Fallback to previous logic: decide separators
    // If contains both '.' and ',' assume European style: '.' thousands, ',' decimal
    if (v.indexOf('.')>-1 && v.indexOf(',')>-1){
      v = v.replace(/\./g,'').replace(',', '.');
      return v;
    }

    // If only one separator present, decide if decimal or thousands
    var lastComma = v.lastIndexOf(',');
    if (lastComma > -1){
      var after = v.substring(lastComma + 1);
      if (/^\d{1,2}$/.test(after)){
        var without = v.substring(0, lastComma).replace(/[\.,]/g,'');
        return without + '.' + after;
      }
    }

    var lastDot = v.lastIndexOf('.');
    if (lastDot > -1){
      var afterDot = v.substring(lastDot + 1);
      if (/^\d{1,2}$/.test(afterDot)){
        var without2 = v.substring(0, lastDot).replace(/[\.,]/g,'');
        return without2 + '.' + afterDot;
      }
    }

    // Otherwise treat all separators as thousands separators -> remove them
    return v.replace(/[\.,]/g,'');
  }

  function formatWithThousandsDot(numberStr){
    if(!numberStr) return '';
    var parts = String(numberStr).split('.');
    var intPart = parts[0] || '0';
    intPart = intPart.replace(/[^0-9]/g,'');
    var decPart = (parts[1] || '').slice(0,2);
    intPart = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    if(decPart.length) return intPart + ',' + decPart;
    return intPart;
  }

  document.addEventListener('DOMContentLoaded', function(){
    // Select input(s) for precio_unitario in admin change form
    var form = document.querySelector('form');
    if(!form) return;
    var priceInput = document.querySelector('input[name="precio_unitario"]');
    if(!priceInput) return;

    // On blur, format visually with dots for thousands and comma for decimals
    priceInput.addEventListener('blur', function(){
      var norm = normalizePriceInput(this.value);
      if(norm === '') return;
      if(!isNaN(norm)){
        this.value = formatWithThousandsDot(norm);
      }
    });

    // On focus, remove formatting to make editing easier
    priceInput.addEventListener('focus', function(){
      var norm = normalizePriceInput(this.value);
      this.value = norm;
    });

    // On form submit, normalize to plain format Django accepts: dot as decimal, no thousand separators
    form.addEventListener('submit', function(){
      var norm = normalizePriceInput(priceInput.value);
      if(norm === '') return; // empty handled by validation
      // Ensure max two decimals
      var m = norm.match(/^(\d+)(\.(\d{1,}))?$/);
      if(m){
        var intp = m[1];
        var dec = (m[3] || '').slice(0,2);
        var final = intp + (dec ? '.' + dec : '');
        priceInput.value = final;
      } else {
        priceInput.value = norm.replace(/[^0-9\.]/g,'');
      }
    });
  });
})();

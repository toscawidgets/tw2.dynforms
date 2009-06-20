/**
 * Cascading
 **/
var twd_cascade_req, twd_cascade_node, twd_cascade_cache = {};
function twd_cascading_onchange(ctrl, ajaxurl, extra, idextra)
{
    if(twd_cascade_cache[ctrl.id][ctrl.value])
        return twd_cascade_apply(ctrl, twd_cascade_cache[ctrl.id][ctrl.value]);
    if(twd_cascade_req)
    {
        alert('A cascade is already in progress; please let it complete before making another.');
        return;
    }
    twd_cascade_node = ctrl;
    if(window.ActiveXObject)
        twd_cascade_req = new ActiveXObject("Microsoft.XMLHTTP");
    else
        twd_cascade_req = new XMLHttpRequest();
    twd_cascade_req.onreadystatechange = twd_cascade_response;
    twd_cascade_req.open("POST", ajaxurl, true);
    twd_cascade_req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded")
    var msg = "value=" + escape(ctrl.value);
    for(i in extra)
        msg = msg + '&' + extra[i] + '=' + escape(twd_find_node(ctrl, extra[i]).value);
    for(i in idextra)
        msg = msg + '&' + idextra[i] + '=' + escape(document.getElementById(idextra[i]).value);
    twd_cascade_req.send(msg);
}

function twd_cascade_response()
{
    if(twd_cascade_req.readyState != 4) return;
    if(twd_cascade_req.status != 200)
    {
        twd_cascade_req = null;
        alert('Server error processing request');
        return;
    }
    var data = eval('x=' + twd_cascade_req.responseText);
    twd_cascade_req = null;
    twd_cascade_apply(twd_cascade_node, data);
}

function twd_cascade_apply(node, data)
{
    for(var n in data)
    {
        var x = twd_find_node(node, n);
        if(x) 
        {
            if(x.className == "ajaxlookup_hidden")
            {
                var entry = document.getElementById(x.id + '_entry');
                entry.value = data[n]['value'];
                twd_set_id(entry, data[n]['id']);
                twd_set_style(entry, 1);
                if(x.onchange) x.onchange();
            }
            else if((x.tagName == "SELECT") && (data[n].constructor.toString().indexOf("Array") != -1))
            {
                x.options.length = 0;
                for(var i = 0; i < data[n].length; i++)
                {
                    if (data[n][i].constructor.toString().indexOf("Array") != -1)
                        x.options[i] = new Option(data[n][i][1], data[n][i][0]);
                    else
                        x.options[i] = new Option(data[n][i], data[n][i]);
                }
            }
            else if(x.tagName == "SPAN")
                x.innerHTML = data[n];
            else 
                x.value = data[n] ? data[n] : '';
        }
    }
}


/**
 * Hiding
 **/
var twd_mapping_store = {};
function twd_hiding_onchange(ctrl)
{
    var cont = document.getElementById(ctrl.id+'.container');
    var is_vis = cont ? cont.style.display != 'none' : 1;
    var mapping = twd_mapping_store[ctrl.id];
    var stem = twd_find_stem(ctrl.id) + '_';

    // Determine the selected value(s)
    var values = [];
    if(ctrl.tagName == 'INPUT' || ctrl.tagName == 'SELECT' || ctrl.tagName == 'TEXTAREA')
        values = [ctrl.type == 'checkbox' ? ctrl.checked : ctrl.value];
    else
        for(var i=0;; i++)
        {
            var cb = document.getElementById(ctrl.id+"_"+i);
            if(!cb) break;
            if(cb.checked)
                values[values.length] = cb.value;
        }

    // Determine all the dependent controls that are visible
    var a, b;
    var visible = {};
    if(is_vis)
        for(a in mapping)
        {
            var match = 0;
            for(b in values)
                if(a == values[b])
                    match = 1;
            if(match)
                for(b in mapping[a])
                    visible[mapping[a][b]] = 1;
        }

    // Set the visibility for all dependent controls, where this has changed
    for(a in mapping)
        for(b in mapping[a])
        {
            var display = visible[mapping[a][b]] ? '' : 'none';
            var x = document.getElementById(stem+mapping[a][b]+'.container');
            if(x.style.display != display)
            {
                x.style.display = display;
                var x = document.getElementById(stem+mapping[a][b]);
                if(x && x.id && twd_mapping_store[x.id])
                    twd_hiding_onchange(x);
            }
        }
}

function twd_hiding_listitem_onchange(ctrl)
{
    twd_hiding_onchange(document.getElementById(
            ctrl.id.substr(0, ctrl.id.lastIndexOf('_'))));
}

function twd_showhide(ctrl, ajaxurl, value_sibling, url_base)
{
    var show = ctrl.src.indexOf('/show') > -1;
    var over = ctrl.src.indexOf('-hover.png') > -1;
    for(var i = 1; 1; i++)
    {
        var node = document.getElementById(ctrl.id + '_' + i);
        if(!node) break;
        node.style.display = show ? '' : 'none';
    }
    if(i == 1 && show && ajaxurl)
    {
        twd_url_base = url_base;
        twd_showhide_ajaxreq(ctrl, ajaxurl, value_sibling);
    }
    ctrl.src = url_base + (show ? '/hide' : '/show') + (over ? '-hover.png' : '.png');
}

function twd_showhide_over(ctrl, url_base)
{
    ctrl.src = url_base + (ctrl.src.indexOf('/show') > -1? '/show-hover.png' : '/hide-hover.png');
}
function twd_showhide_out(ctrl, url_base)
{
    ctrl.src = url_base + (ctrl.src.indexOf('/show') > -1? '/show.png' : '/hide.png');
}

var twd_proc_req = null;
function twd_showhide_ajaxreq(ctrl, ajaxurl, value_sibling)
{
    if(twd_proc_req)
    {
        alert('A server request is already in progress; please let it complete before making another.');
        return;
    }
    twd_popup_node = ctrl;
    if(window.ActiveXObject)
        twd_proc_req = new ActiveXObject("Microsoft.XMLHTTP");
    else
        twd_proc_req = new XMLHttpRequest();
    twd_proc_req.onreadystatechange = twd_showhide_ajaxcb;
    twd_proc_req.open("POST", ajaxurl, true);
    twd_proc_req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded")
    value = value_sibling ? twd_find_node(ctrl, value_sibling).value : '';    
    twd_proc_req.send("value="+value);
}

function twd_showhide_ajaxcb()
{    
    if(twd_proc_req.readyState != 4) return;
    if(twd_proc_req.status != 200)
    {
        twd_proc_req = null;
        alert('Server error processing request');
        return;
    }
    twd_popup_elem = document.createElement('TR');
    twd_popup_elem.id = twd_popup_node.id + '_1';
    twd_popup_elem.appendChild(document.createElement('TD'));
    twd_popup_elem.firstChild.colSpan = 10; // This should be wide enough to cover all tables in practice
    twd_popup_elem.firstChild.innerHTML = twd_proc_req.responseText;
       
    var tr_node = twd_popup_node;
    while(tr_node.tagName != 'TR')
        tr_node = tr_node.parentNode;
    tr_node.parentNode.insertBefore(twd_popup_elem, tr_node.nextSibling);

    var namer = document.getElementById(twd_popup_node.id + '_namer');
    var name_prefix = namer.name.substr(0, namer.name.lastIndexOf(".") + 1);
    var id_prefix = namer.id.substr(0, namer.id.lastIndexOf("_") + 1);
    var x = twd_get_all_nodes(twd_popup_elem)
    for(var i = 1; i < x.length; i++) // start at 1 to avoid rewriting the root node
    {        
        if(x[i].id) x[i].id = id_prefix + x[i].id;
        if(x[i].name) x[i].name = name_prefix + x[i].name;
    }
    
    twd_popup_node.src = twd_url_base + '/hide.png';
    twd_proc_req = null;
}

/***
 * Growing
 **/
function twd_grow_add(ctrl, desc)
{
    // Find the id/name prefixes, and the next number in sequence
    if(ctrl.id.indexOf('_grow-') > -1)
    {
        // autogrow
        var autogrow = 1;
        var idprefix = ctrl.id.substring(0, ctrl.id.lastIndexOf('_grow-'));
        var nameprefix = ctrl.name.substring(0, ctrl.name.lastIndexOf('grow-'));
    }
    else
    {
        // button grow
        var autogrow = 0;
        var idprefix = ctrl.id.substring(0, ctrl.id.lastIndexOf('_add'));
        var nameprefix = ctrl.name.substring(0, ctrl.name.lastIndexOf('add'));
    }    
    var node = document.getElementById(idprefix + '_repeater').firstChild;
    var lastnode = null;
    while(node)
    {
        if(node.id && node.id.indexOf(idprefix + '_grow-') == 0)
            lastnode = node;
        node = node.nextSibling;
    }
    var number = lastnode ? parseInt(lastnode.id.substr(idprefix.length + 6)) + 1 : 0;

    // Only autogrow if we are the last row
    if(autogrow && parseInt(ctrl.id.substr(idprefix.length + 6)) != number-1)
        return;
        
    // Clone the spare element; update id and name attributes; include in page
    var old_elem = document.getElementById(idprefix + '_spare');
    var elem = old_elem.cloneNode(true);
    var id_stemlen = idprefix.length + 6;
    var name_stemlen = nameprefix.length + 5;
    var new_name_prefix = nameprefix + 'grow-' + number;
    var new_id_prefix = idprefix + '_grow-' + number;
    var x = twd_get_all_nodes(elem)
    var calendars = [];
    for(var i = 0; i < x.length; i++)
    {
        if(x[i].name) x[i].name = new_name_prefix + x[i].name.substr(name_stemlen);
        if(x[i].id)
        {
            x[i].id = new_id_prefix + x[i].id.substr(id_stemlen);
            if(x[i].id.substr(x[i].id.length - 8) == '_trigger')
                calendars[calendars.length] = x[i].id.substr(0, x[i].id.length - 8);
        }
        if(x[i].tagName == 'LEGEND') x[i].innerHTML = x[i].innerHTML.replace('$$', number+1);
    }
    document.getElementById(idprefix + '_repeater').insertBefore(elem,
            document.getElementById(idprefix + '_sparecont'));

    // Make the delete button visible, and any HidingButton widgets
    if(autogrow)
    {
        var del = document.getElementById(idprefix + '_grow-' + (number-1) + '_del');
        if(del) del.style.display = '';
        var x = twd_get_all_nodes(document.getElementById(idprefix + '_grow-' + (number-1)));
        for(var i = 0; i < x.length; i++)
            if(x[i].tagName == 'IMG' && x[i].src.indexOf('/show.png')) x[i].style.display = '';
    }
    
    // Clone any stored mappings for hiding fields
    for(id in twd_mapping_store)
        if(id.indexOf(idprefix + '_spare') == 0)
            twd_mapping_store[new_id_prefix + id.substr(id_stemlen)] = twd_mapping_store[id];
    
    // Setup calendars        
    for(var i in calendars)
        Calendar.setup({"ifFormat": "%d\/%m\/%Y", "button": calendars[i]+"_trigger", "showsTime": false, "inputField": calendars[i]});
}

var twd_grow_undo_data = {};
function twd_grow_del(ctrl)
{
    var idprefix = ctrl.id.substring(0, ctrl.id.lastIndexOf('_grow-'));
    var rowid = ctrl.id.substring(0, ctrl.id.indexOf('_', idprefix.length+6));
    if(!twd_grow_undo_data[idprefix]) twd_grow_undo_data[idprefix] = [];
    twd_grow_undo_data[idprefix].push(rowid);
    nodes = twd_get_all_nodes(document.getElementById(rowid));
    for(var i = 0; i < nodes.length; i++)
        if(nodes[i].tagName == 'IMG' && nodes[i].src.indexOf('/hide.png') > -1)
            nodes[i].onclick();    
    document.getElementById(rowid).style.display = 'none';
    document.getElementById(idprefix + '_undo').style.display = '';
}

function twd_grow_undo(ctrl)
{
    var idprefix = ctrl.id.substring(0, ctrl.id.length-5);
    document.getElementById(twd_grow_undo_data[idprefix].pop()).style.display = '';
    if(!twd_grow_undo_data[idprefix].length) ctrl.style.display = 'none';
}

/**
 * Link container
 **/
function twd_link_onchange(ctrl)
{
    var visible = ctrl.style.display != 'none';
    var view = document.getElementById(ctrl.id + '_view')
    view.style.display = visible && ctrl.value ? '' : 'none';
}

function twd_link_view(ctrl, link, popup_options)
{
    var value = document.getElementById(ctrl.id.substr(0, ctrl.id.length-5)).value;
    window.open(link.replace(/\$/, value), '_blank', popup_options);
    return false;
}

/**
 * Utility functions
 **/
function twd_blank_deleted()
{
    for(var g in twd_grow_undo_data)
        for(var c in twd_grow_undo_data[g])
        {
            var x = twd_get_all_nodes(document.getElementById(twd_grow_undo_data[g][c]));
            for(var i = 0; i < x.length; i++)
                if(x[i].tagName == 'INPUT' || x[i].tagName == 'SELECT' || x[i].tagName == 'TEXTAREA')
                    x[i].value = '';
        }
}

function twd_get_all_nodes(elem)
{
    var ret = [elem];
    for(var node = elem.firstChild; node; node = node.nextSibling)
        ret = ret.concat(twd_get_all_nodes(node))
    return ret;
}

function twd_suppress_enter(evt) {
    var evt = (evt) ? evt : ((event) ? event : null);
    var node = (evt.target) ? evt.target : ((evt.srcElement) ? evt.srcElement : null);
    if (evt.keyCode == 13)  {return node.type == 'textarea';}
}

function twd_find_node(node, suffix)
{
    var prefix = node.id.substr(0, node.id.lastIndexOf("_") + (suffix ? 1 : 0));
    return document.getElementById(prefix + suffix);
}

function twd_no_multi_submit(ctrl) 
{
    ctrl.disabled = 1;
    var form = twd_find_node(ctrl, '');
    if(form.onsubmit) form.onsubmit();
    form.submit();
    return false;
}

function twd_find_stem(ctrlid)
{
    var pos = ctrlid.lastIndexOf('_');
    if(pos == -1) return '';
    var stem = ctrlid.substr(0, pos);
    if(document.getElementById(stem))
        return stem;
    else    
        return twd_find_stem(stem);
}

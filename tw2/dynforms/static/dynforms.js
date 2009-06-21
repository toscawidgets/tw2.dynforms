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
            var cb = document.getElementById(ctrl.id+":"+i);
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


/***
 * Growing
 **/
function twd_grow_add(ctrl)
{
    var parent_id = ctrl.id.substring(0, ctrl.id.lastIndexOf(':'));
    var id_prefix = parent_id.substring(0, parent_id.lastIndexOf(':'));
    var next_num;
    for(next_num = 0; document.getElementById(id_prefix + ':' + next_num); next_num++) {}
    var this_num = parseInt(parent_id.substr(parent_id.lastIndexOf(':')+1));
    if(this_num != next_num - 2)
        return;
    var node = document.getElementById(id_prefix + ':0').cloneNode(true);

    var stemlen = id_prefix.length + 2;
    var new_prefix = id_prefix + ':' + next_num;
    var x = twd_get_all_nodes(node)
    for(var i = 0; i < x.length; i++)
    {
        if(x[i].name) x[i].name = new_prefix + x[i].name.substr(stemlen);
        if(x[i].id) x[i].id = new_prefix + x[i].id.substr(stemlen);
    }
    var last_node = document.getElementById(id_prefix + ':' + (next_num - 1));
    last_node.appendSibling(node);

    var del = document.getElementById(id_prefix + ':_del');
    if(del) del.style.display = '';
}

var twd_grow_undo_data = {};
function twd_grow_del(ctrl)
{
    var parent_id = ctrl.id.substring(0, ctrl.id.lastIndexOf(':'));
    var id_prefix = parent_id.substring(0, parent_id.lastIndexOf(':'));
    if(!twd_grow_undo_data[id_prefix]) twd_grow_undo_data[id_prefix] = [];
    twd_grow_undo_data[id_prefix].push(parent_id);
    document.getElementById(parent_id).style.display = 'none';
    document.getElementById(id_prefix + ':undo').style.display = '';
}

function twd_grow_undo(ctrl)
{
    var id_prefix = ctrl.id.substring(0, ctrl.id.lastIndexOf(':'));
    document.getElementById(twd_grow_undo_data[id_prefix].pop()).style.display = '';
    if(!twd_grow_undo_data[id_prefix].length) ctrl.style.display = 'none';
}

/**
 * Link container
 **/
function twd_link_onchange(ctrl, link)
{
    var view = document.getElementById(ctrl.id + ':view')
    view.style.display = ctrl.value ? '' : 'none';
    view.href = link.replace(/\$/, ctrl.value)
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

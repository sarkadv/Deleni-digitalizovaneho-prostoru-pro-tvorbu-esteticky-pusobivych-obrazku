# Test helpers for the GUI tests, shared by the Python program (tkinter) and the C program (Tcl/Tk C API).
#
# The UI driver (tests/ui/drivers.py) loads this file into the application's own Tcl interpreter.
# The helpers find widgets the way a user does - by their kind (Tk class) and visible text, never by
# widget path names - and replace the Tk dialog commands, so tests choose files and read messages
# without real dialogs. The program's code is not changed.
#
# All results are Tcl lists / dicts of plain strings.

namespace eval ::uidriver {
    # queued answers of the replaced dialogs: answers(open), answers(save), answers(message)
    variable answers
    array set answers {open {} save {} message {}}
    # every replaced dialog call: {kind options}, kind = open | save | message
    variable log {}

    # widget classes a user can press
    variable clickable {Button Checkbutton Radiobutton TButton TCheckbutton TRadiobutton}
}

# ---- replaced dialogs ---------------------------------------------------------------------------

proc ::uidriver::dialog {kind opts} {
    variable answers
    variable log
    lappend log [list $kind $opts]
    if {[llength $answers($kind)] == 0} {
        if {$kind ne "message"} {
            return ""                     ;# like pressing Cancel in a file dialog
        }
        return [default_button $opts]
    }
    set answer [lindex $answers($kind) 0]
    set answers($kind) [lrange $answers($kind) 1 end]
    return $answer
}

proc ::uidriver::default_button {opts} {
    if {[dict exists $opts -default]} {
        return [dict get $opts -default]
    }
    set type ok
    if {[dict exists $opts -type]} {
        set type [dict get $opts -type]
    }
    return [dict get {ok ok okcancel ok yesno yes yesnocancel yes retrycancel retry
                      abortretryignore abort} $type]
}

proc ::tk_getOpenFile {args} { ::uidriver::dialog open $args }
proc ::tk_getSaveFile {args} { ::uidriver::dialog save $args }
proc ::tk_messageBox {args} { ::uidriver::dialog message $args }

# answer(kind, value): the next dialog of this kind returns value (file path, "" = Cancel, message button)
proc ::uidriver::answer {kind value} {
    variable answers
    lappend answers($kind) $value
    return ""
}

# log(): all dialog calls since the last clear_log, oldest first
proc ::uidriver::log {} {
    variable log
    return $log
}

proc ::uidriver::clear_log {} {
    variable log
    set log {}
    return ""
}

# ---- finding widgets ----------------------------------------------------------------------------

# all widgets in the tree under w (w included)
proc ::uidriver::tree {{w .}} {
    set result [list $w]
    foreach child [winfo children $w] {
        lappend result {*}[tree $child]
    }
    return $result
}

proc ::uidriver::is_toplevel {w} {
    return [expr {[winfo toplevel $w] eq $w}]
}

# Is the toplevel window shown on the screen (not withdrawn or iconified)?
proc ::uidriver::window_shown {top} {
    return [expr {[winfo exists $top] && [wm state $top] in {normal zoomed}}]
}

# Does a later (= higher in the stacking order) managed sibling cover the centre of w?
# This is how a frame lowered under another frame in the same grid cell is hidden.
proc ::uidriver::covered {w} {
    set siblings [winfo children [winfo parent $w]]
    set cx [expr {[winfo x $w] + [winfo width $w] / 2}]
    set cy [expr {[winfo y $w] + [winfo height $w] / 2}]
    foreach s [lrange $siblings [lsearch -exact $siblings $w]+1 end] {
        if {[is_toplevel $s] || [winfo manager $s] eq ""} {
            continue
        }
        set x [winfo x $s]
        set y [winfo y $s]
        if {$cx >= $x && $cx < $x + [winfo width $s] && $cy >= $y && $cy < $y + [winfo height $s]} {
            return 1
        }
    }
    return 0
}

# Can a user see w? Its window is shown, w and all its parents are placed by a geometry manager
# and none of them is hidden under a sibling.
proc ::uidriver::shown {w} {
    if {![winfo exists $w]} {
        return 0
    }
    set top [winfo toplevel $w]
    if {![window_shown $top]} {
        return 0
    }
    for {set cur $w} {$cur ne $top} {set cur [winfo parent $cur]} {
        if {[winfo manager $cur] eq "" || [covered $cur]} {
            return 0
        }
    }
    return 1
}

# Can a user operate w? Shown, and inside the grab window if some window holds a grab
# (a modal window such as the result window blocks the rest of the application).
proc ::uidriver::reachable {w} {
    if {![shown $w]} {
        return 0
    }
    foreach g [grab current] {
        if {$w ne $g && ![string match "$g.*" $w]} {
            return 0
        }
    }
    return 1
}

proc ::uidriver::option {w name} {
    if {[catch {$w cget $name} value]} {
        return ""
    }
    return $value
}

proc ::uidriver::global_value {name} {
    if {$name eq "" || [catch {uplevel #0 [list set $name]} value]} {
        return ""
    }
    return $value
}

# The text a user reads on w (the value of its -textvariable if it has one).
proc ::uidriver::text {w} {
    set var [option $w -textvariable]
    if {$var ne ""} {
        return [global_value $var]
    }
    return [option $w -text]
}

# value: 1/0 for a (un)checked check button, "" otherwise
proc ::uidriver::value {w} {
    if {[winfo class $w] ni {Checkbutton TCheckbutton}} {
        return ""
    }
    set on [option $w -onvalue]
    if {$on eq ""} {
        set on 1
    }
    return [expr {[global_value [option $w -variable]] eq $on}]
}

proc ::uidriver::describe {w} {
    set top [winfo toplevel $w]
    return [dict create path $w class [winfo class $w] text [text $w] value [value $w] \
                state [option $w -state] window [wm title $top] \
                x [expr {[winfo rootx $w] - [winfo rootx $top]}] \
                y [expr {[winfo rooty $w] - [winfo rooty $top]}] \
                width [winfo width $w] height [winfo height $w]]
}

# widgets ?title?: every shown widget (of the window with this title), as dicts
#   {path class text value state window x y width height}; x, y relative to the window
proc ::uidriver::widgets {args} {
    update idletasks
    set result {}
    foreach w [tree] {
        if {[is_toplevel $w] || ![shown $w]} {
            continue
        }
        if {[llength $args] && [wm title [winfo toplevel $w]] ne [lindex $args 0]} {
            continue
        }
        lappend result [describe $w]
    }
    return $result
}

# windows: every shown toplevel window (menus excluded) as {path title width height}
proc ::uidriver::windows {} {
    update idletasks
    set result {}
    foreach w [tree] {
        if {[is_toplevel $w] && [winfo class $w] ne "Menu" && [window_shown $w]} {
            lappend result [dict create path $w title [wm title $w] \
                                width [winfo width $w] height [winfo height $w]]
        }
    }
    return $result
}

# find text ?classes?: the one shown widget with exactly this text (and one of these classes)
proc ::uidriver::find {text {classes {}}} {
    update idletasks
    set found {}
    foreach w [tree] {
        if {[is_toplevel $w] || ![shown $w]} {
            continue
        }
        if {[llength $classes] && [winfo class $w] ni $classes} {
            continue
        }
        if {[text $w] eq $text} {
            lappend found $w
        }
    }
    if {[llength $found] == 0} {
        error "no shown widget with text \"$text\" (classes: $classes)"
    }
    if {[llength $found] > 1} {
        error "more than one shown widget with text \"$text\": $found"
    }
    return [lindex $found 0]
}

proc ::uidriver::require_reachable {w} {
    if {![reachable $w]} {
        error "widget \"[text $w]\" cannot be operated: another window holds the grab"
    }
    if {[option $w -state] eq "disabled"} {
        error "widget \"[text $w]\" is disabled"
    }
}

# ---- user actions -------------------------------------------------------------------------------
# Each action ends with the widget's invoke: the invoked command may destroy the whole application
# (the Python program's reset), so nothing may run after it.

# click text: press the button / check button with this text
proc ::uidriver::click {text} {
    variable clickable
    set w [find $text $clickable]
    require_reachable $w
    $w invoke
}

# The menu of an option menu (a menubutton showing its current value).
proc ::uidriver::option_menu {menu_text} {
    set w [find $menu_text {Menubutton TMenubutton}]
    return [list $w [$w cget -menu]]
}

# menu_items menu_text: the item labels of the option menu that currently shows menu_text
proc ::uidriver::menu_items {menu_text} {
    lassign [option_menu $menu_text] w menu
    set items {}
    if {[$menu index end] eq "none"} {
        return $items
    }
    for {set i 0} {$i <= [$menu index end]} {incr i} {
        if {[$menu type $i] in {command radiobutton checkbutton}} {
            lappend items [$menu entrycget $i -label]
        }
    }
    return $items
}

# choose menu_text item: open the option menu that shows menu_text and choose item
proc ::uidriver::choose {menu_text item} {
    lassign [option_menu $menu_text] w menu
    require_reachable $w
    set index ""
    for {set i 0} {$i <= [$menu index end]} {incr i} {
        if {[$menu type $i] in {command radiobutton checkbutton} && [$menu entrycget $i -label] eq $item} {
            set index $i
        }
    }
    if {$index eq ""} {
        error "menu \"$menu_text\" has no item \"$item\""
    }
    $menu invoke $index
}

# close_window title: close the window with this title as the window manager's close button does
proc ::uidriver::close_window {title} {
    foreach w [tree] {
        if {[is_toplevel $w] && [window_shown $w] && [wm title $w] eq $title} {
            set command [wm protocol $w WM_DELETE_WINDOW]
            if {$command eq ""} {
                destroy $w
                return
            }
            uplevel #0 $command
            return
        }
    }
    error "no shown window with title \"$title\""
}

# ---- canvas and images --------------------------------------------------------------------------

# canvas_images ?title?: image items of shown canvases as {image x y anchor width height}
# (x, y = the item's anchor point in canvas coordinates; width, height = size of the shown image)
proc ::uidriver::canvas_images {args} {
    set result {}
    foreach w [tree] {
        if {[winfo class $w] ne "Canvas" || ![shown $w]} {
            continue
        }
        if {[llength $args] && [wm title [winfo toplevel $w]] ne [lindex $args 0]} {
            continue
        }
        foreach id [$w find all] {
            if {[$w type $id] ne "image"} {
                continue
            }
            set image [$w itemcget $id -image]
            lassign [$w coords $id] x y
            lappend result [dict create image $image x [expr {round($x)}] y [expr {round($y)}] \
                                anchor [$w itemcget $id -anchor] \
                                width [image width $image] height [image height $image]]
        }
    }
    return $result
}

# image_pixel image x y: {r g b} of a pixel of a Tk photo image
proc ::uidriver::image_pixel {image x y} {
    return [$image get $x $y]
}

set ::uidriver::loaded 1

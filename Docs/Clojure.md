## Zephyros - Clojure API

#### Setup

* Install leiningen if need be: `brew install leiningen`
* Add this to ~/.lein/profiles.clj: `{:user {:plugins [[lein-exec "0.3.0"]]}}`

#### Sample script

* Put this in `my-zeph.clj` somewhere:

```clojure
(use '[leiningen.exec :only (deps)])
(deps '[[org.clojure/data.json "0.2.2"]])

(load-file "/Applications/Zephyros.app/Contents/Resources/libs/zephyros.clj")

(bind "D" ["Cmd" "Shift"]
      (fn []
        (alert "hello world" 1)
        (let [win (get-focused-window)
              f (get-frame win)
              f (update-in f [:x] + 10)]
          (set-frame win f))))

(bind "F" ["Cmd" "Shift"]
      (fn []
        (alert "hello world" 1)))

@listen-for-callbacks
```

#### Run

```bash
lein exec path/to/my-zeph.clj
```

#### API

The function `bind` and `unbind` uses this [key strings and modifiers](https://github.com/sdegutis/zephyros/blob/master/Zephyros/SDKeyBindingTranslator.m#L148).

The function `update-settings` uses this [keys and values](Protocol.md#note-3-update-settings-keys).

```clojure
;; top level

(defn bind [key mods f]) ;; see note above
(defn unbind [key mods]) ;; see note above

(defn listen [event f])
(defn unlisten [event])
  ;; Valid events and their param-lists:
  ;;
  ;; 'window_created' args: [win]
  ;; 'window_minimized' args: [win]
  ;; 'window_unminimized' args: [win]
  ;; 'window_moved' args: [win]
  ;; 'window_resized' args: [win]
  ;; 'app_launched' args: [app]
  ;; 'app_died' args: [app]
  ;; 'app_hidden' args: [app]
  ;; 'app_shown' args: [app]
  ;; 'screens_changed' args: []
  ;; 'mouse_moved' args: [movement] (see Protocol.md for details)
  ;; 'modifiers_changed' args: [mods] (see Protocol.md for details)


(defn get-focused-window [])
(defn get-visible-windows [])
(defn get-all-windows [])

(defn update-settings [s]) ;; map - see note above

(defn get-main-screen [])
(defn get-all-screens [])

(defn get-running-apps [])

(defn show-box [msg])
(defn hide-box [])

(defn alert [msg duration])
(defn log [msg])
(defn choose-from [list title f]) ;; f receives chosen idx or nil if canceled

(defn relaunch-config [])
(defn get-clipboard-contents [])

(defn undo [])
(defn redo [])


;; window

(defn get-window-title [window])

(defn get-frame [window])       ;; returns {:x, :y, :w, :h}
(defn get-size [window])        ;; returns {:w, :h}
(defn get-top-left [window])    ;; returns {:w, :h}

(defn set-frame [window f])     ;; takes {:x, :y, :w, :h}
(defn set-size [window s])      ;; takes {:w, :h}
(defn set-top-left [window tl]) ;; takes {:x, :y}

(defn minimize [window])
(defn maximize [window])
(defn un-minimize [window])

(defn get-app-for-window [window])
(defn get-screen-for-window [window])

(defn focus-window [window]) ;; returns bool

(defn focus-window-left [window])
(defn focus-window-right [window])
(defn focus-window-up [window])
(defn focus-window-down [window])

(defn windows-to-north [window])
(defn windows-to-south [window])
(defn windows-to-west [window])
(defn windows-to-east [window])

(defn normal-window? [window])
(defn minimized? [window])


;; app

(defn visible-windows-for-app [app])
(defn all-windows-for-app [app])

(defn get-app-title [app])
(defn app-hidden? [app])

(defn show-app [app])
(defn hide-app [app])

(defn kill-app [app])
(defn kill9-app [app])


;; screeen

(defn screen-frame-including-dock-and-menu [screen]) ;; returns {:x, :y, :w, :h}
(defn screen-frame-without-dock-or-menu [screen])    ;; returns {:x, :y, :w, :h}

(defn next-screen [screen])
(defn previous-screen [screen])
(defn rotate-to [screen degrees])


;; any resource type

(defn retain [resource])
(defn release [resource])

;; These methods must be used when you want to keep a refernce around longer than a single callback.
;; Retain increments the retain-count and release decrements it. When it reaches 0, it will be garbage-collected after 5 seconds.
;; When you first get a resource back, it starts with a retain-count of 0.
```

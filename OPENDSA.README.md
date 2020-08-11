### githib submodeles

see opendsa readme

### codio custom assessments

append string
```js
if (score.correct) {
    var taskId = 'custom-' + Khan.currentExerciseId.toLowerCase();
    window.parent.postMessage(JSON.stringify({
      taskId: taskId,
      status: 'done'
    }), '*');
}
```
before
```js
  $(Exercises).trigger("problemDone", {
```

in file `OpenDSA/khan-exercises/interface.js`

Also need some patching for run in different domain/subdomain

`lib/odsaKA.js` `lib/odsaKA-min.js`

```js
// MODULE_ORIGIN = parent.location.protocol + '//' + parent.location.host,
MODULE_ORIGIN = 'https://global.codio.com',
```

`lib/odsaMOD.js` `lib/odsaMOD-min.js`
```js
// var url = (window.location != window.parent.location) ? document.referrer : document.location;
var url = document.referrer;
```

`khan-exercise.js`

delete lines
```js
// Hook out for exercise test runner
if (localMode && parent !== window && typeof parent.jQuery !== "undefined") {
   parent.jQuery(parent.document).trigger("problemLoaded", [makeProblem, answerData.solution]);
}
```

Do not forget add codio client script file

```yaml
metadata:
  scripts:
    - https://codio.com/codio-client.js
    - https://global.codio.com/opendsa/passtocodio_v2.js
```

### Copy assets instructions

```yml
assets:
  - SourceCode
  - "DataStructures":
      pattern: "*.js"
      dst: ".guides/opendsa_v1/DataStructures"
  - "DataStructures":
      pattern: "*.css"
      dst: ".guides/opendsa_v1/DataStructures"
  - "Exercises":
      pattern: "*.js"
      dst: ".guides/opendsa_v1/Exercises"
  - "Exercises":
      pattern: "*.html"
      dst: ".guides/opendsa_v1/Exercises"
  - "Exercises":
      pattern: "*.json"
      dst: ".guides/opendsa_v1/Exercises"
  - "AV":
      pattern: "*.js"
      dst: ".guides/opendsa_v1/AV"
  - "AV":
      pattern: "*.html"
      dst: ".guides/opendsa_v1/AV"
  - "AV":
      pattern: "*.json"
      dst: ".guides/opendsa_v1/AV"
  - "AV":
      pattern: "*.css"
      dst: ".guides/opendsa_v1/AV"
  - "lib":
      pattern: "*.js"
      dst: ".guides/opendsa_v1/lib"
  - "lib":
      pattern: "*.html"
      dst: ".guides/opendsa_v1/lib"
  - "lib":
      pattern: "*.json"
      dst: ".guides/opendsa_v1/lib"
  - "lib":
      pattern: "*.png"
      dst: ".guides/opendsa_v1/lib"
  - "lib":
      pattern: "*.css"
      dst: ".guides/opendsa_v1/lib"
  - "khan-exercises":
      pattern: "*.js"
      dst: ".guides/opendsa_v1/khan-exercises"
  - "khan-exercises":
      pattern: "*.css"
      dst: ".guides/opendsa_v1/khan-exercises"
  - "khan-exercises":
      pattern: "*.html"
      dst: ".guides/opendsa_v1/khan-exercises"
  - "khan-exercises":
      pattern: "*.png"
      dst: ".guides/opendsa_v1/khan-exercises"
  - "khan-exercises":
      pattern: "*.gif"
      dst: ".guides/opendsa_v1/khan-exercises"
  - "khan-exercises":
      pattern: "*.eot"
      dst: ".guides/opendsa_v1/khan-exercises"
  - "khan-exercises":
      pattern: "*.otf"
      dst: ".guides/opendsa_v1/khan-exercises"
  - "khan-exercises":
      pattern: "*.svg"
      dst: ".guides/opendsa_v1/khan-exercises"
  - "khan-exercises":
      pattern: "*.woff"
      dst: ".guides/opendsa_v1/khan-exercises"
optimization:
  optimizeImages: true
```


### JSAV images

To make assets add to config lines 
```
opendsa:
  writeIframe: true
```

In generate folder will appear subfolder with name `jsav` - upload it to base CDN path 

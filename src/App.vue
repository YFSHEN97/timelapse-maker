<template>
  <v-app style="background:#272727">
    <!-- Top navigation bar -->
    <v-app-bar app clipped-left clipped-right dark color="#1e1e1e">
      <v-toolbar-title class="headline">
        <span class="ml-4">TimelapseMaker</span>
      </v-toolbar-title>
    </v-app-bar>

    <!-- Left navigation bar for the ordering of images-->
    <v-navigation-drawer app clipped permanent dark color="#1e1e1e">
      <draggable
        class="list-group"
        v-model="list"
        v-bind="dragOptions"
        @start="drag = true"
        @end="drag = false"
      >
        <transition-group>
          <v-list-item
            v-for="element in list"
            :key="element.key"
            @mousedown="selected=element; video_view=false"
          >
            <v-list-item-avatar tile size=80>
              <v-img :src="element.src"></v-img>
            </v-list-item-avatar>
            <v-list-item-content>
              <v-list-item-title v-text="element.name"></v-list-item-title>
              <v-list-item-subtitle>Age: {{ (element.age == -1) ? "N/A" : String(element.age) + " years" }}</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </transition-group>
      </draggable>
    </v-navigation-drawer>

    <!-- Right navigation bar for control tabs -->
    <v-navigation-drawer app right clipped permanent dark width="350" color="#1e1e1e">
    <v-container>
      <span class="subheading font-weight-medium white--text ml-4">ORGANIZE IMAGES</span>
      <!-- Button for adding image(s) -->
      <v-btn dark block left class="py-0 mt-4" @click="import_image()">
        <v-icon left class="mr-2">add_photo_alternate</v-icon>
        <span>Add New Image</span>
        <input multiple type="file" id="open_image" accept=".jpg,.jpeg,.png,.bmp" @change="add_image" style="display: none">
      </v-btn>
      <!-- Button for removing image -->
      <v-btn dark block left class="py-0 mt-1" @click="remove_image()">
        <v-icon left class="mr-2">mdi-image-remove</v-icon>
        <span>Remove Image</span>
      </v-btn>
      <!-- Button for estimating age -->
      <v-btn dark block left class="py-0 mt-1" @click="estimate_age()">
        <v-icon left class="mr-2">mdi-face-recognition</v-icon>
        <span>Estimate Age for Selected</span>
      </v-btn>
      <!-- Button for estimating age for all undefined -->
      <v-btn dark block left class="py-0 mt-1" @click="estimate_age_all()">
        <v-icon left class="mr-2">mdi-face-woman-shimmer-outline</v-icon>
        <span>Estimate Age for All</span>
      </v-btn>
      <!-- Button for sorting images by age -->
      <v-btn dark block left class="py-0 mt-1" @click="sort_images()">
        <v-icon left class="mr-2">mdi-drama-masks</v-icon>
        <span>Sort Images by Age</span>
      </v-btn>
      <!-- Text field for manually specifying age -->
      <v-container><span class="white--text">Enter age for selected: </span>
      <input
        v-model="selected.age"
        :disabled="selected.key==0"
        type="number"
        placeholder="Age"
        style="width: 45px; margin-left: 15px; color: white"
      ><span class="white--text"> years old</span>
      </v-container>

      <v-divider class="mt-2 mb-4" />
      <span class="subheading font-weight-medium white--text ml-4">GENERATE TIMELAPSE</span>
      <!-- Radio buttons for selecting jump-cut/cross-fading -->
      <v-container>
      <span class="white--text ml-1">Select Mode for Face Transitions</span>
      <v-radio-group row v-model="transition_type">
        <v-row align="center" justify="space-around">
          <v-radio label="Jump-Cut" value="jump-cut" />
          <v-radio label="Cross-Fading" value="cross-fading" />
        </v-row>
      </v-radio-group>
      <!-- Radio buttons for selecting FPS -->
      <span class="white--text ml-1">Select Frame Rate for Output Video</span>
      <v-radio-group row v-model="fps">
        <v-row align="center" justify="space-around">
          <v-radio label="24" value="24" />
          <v-radio label="30" value="30" />
          <v-radio label="60" value="60" />
        </v-row>
      </v-radio-group>
      <!-- Text field for pausing time for each face; default 1 second -->
      <span class="white--text">Pause for each face: </span>
      <input
        v-model="pause"
        type="number"
        placeholder="Pause"
        style="width: 45px; margin-left: 15px; color: white"
      ><span class="white--text"> seconds</span><br>
      <!-- Text field for morphing time; disabled unless cross-fading; default 1 second -->
      <span class="white--text">Duration for cross-fade: </span>
      <input
        v-model="fade_duration"
        :disabled="transition_type=='jump-cut'"
        type="number"
        placeholder="Pause"
        style="width: 45px; margin-left: 15px; color: white"
      ><span class="white--text"> seconds</span>
      </v-container>
      <!-- Button for rendering video -->
      <v-btn dark block left class="py-0 mt-1" :disabled="list.length < 2" @click="render_video()">
        <v-icon left class="mr-2">mdi-video-vintage</v-icon>
        <span>Render with Current Settings</span>
      </v-btn>
      <!-- Button for playing most recently rendered video -->
      <v-btn dark left class="py-0 mt-1" :disabled="video_src==undefined" @click="play_video()">
        <v-icon left class="mr-2">play_circle_outline</v-icon>
        <span>Play Newest</span>
      </v-btn>
      <!-- Button for saving most recently rendered video -->
      <v-btn dark right class="py-0 ml-1 mt-1" width="160" :disabled="video_src==undefined" @click="save_video()">
        <v-icon left class="mr-2">mdi-file-video</v-icon>
        <span>Save</span>
      </v-btn>
    </v-container>
    </v-navigation-drawer>

    <!-- Middle section for displaying selected image -->
    <v-main>
      <v-container>
        <v-row v-if="!video_view" class="text-center">
          <v-col cols="12"><v-img :src="selected.src" contain height="550"/></v-col>
          <v-col><h3 class="white--text">Apparent age: {{ (selected.age == -1) ? "N/A" : String(selected.age) + " years" }}</h3></v-col>
        </v-row>
        <v-row v-else class="text-center">
          <v-col cols="12"><video id="video" width="800" height="600" controls>
            <source :src="video_src" type='video/mp4'>
              Your browser does not support HTML video.
          </video></v-col>
        </v-row>
      </v-container>
    </v-main>

    <!-- Messages to tell user to wait -->
    <v-snackbar v-model="working" light :timeout="-1">
      Working, please wait...
    </v-snackbar>
  </v-app>
</template>

<script>
import draggable from 'vuedraggable'
import axios from 'axios'

export default {
  name: "TimelapseMaker",
  components: {
    draggable
  },
  data() {
    return {
      transition_type: "jump-cut",
      fps: "30",
      pause: 1,
      fade_duration: 1,
      default_src: require("./assets/undefined.jpeg"),
      selected: {
        name: "undefined",
        src: require("./assets/undefined.jpeg"),
        age: -1,
        key: 0
      },
      list: [],
      drag: false,
      working: false,
      video_view: false,
      video_src: undefined
    };
  },
  computed: {
    dragOptions() {
      return {
        animation: 200,
        group: "description",
        disabled: false,
        ghostClass: "ghost"
      };
    }
  },
  methods: {
    // triggered when the add image button is clicked
    import_image() {
      document.getElementById('open_image').click();
    },
    add_image(e) {
      let images = e.target.files || e.dataTransfer.files;
      if (!images.length) return;
      for (let i = 0; i < images.length; i++) {
        if (typeof images[i] == 'undefined') continue;
        let fr = new FileReader();
        let list = this.list;
        fr.onload = function(e) {
          list.push({
            name: images[i].name,
            src: e.target.result,
            age: -1,
            key: list.length + 1
          });
        };
        fr.readAsDataURL(images[i]);
      }
    },
    // triggered when the remove image button is clicked
    remove_image() {
      if (this.selected.key == 0) return;
      for (let i = 0; i < this.list.length; i++) {
        if (this.list[i].key == this.selected.key) {
          this.list.splice(i, 1);
          break;
        }
      }
      for (let i = 0; i < this.list.length; i++) {
        this.list[i].key = i + 1;
      }
      this.selected = {
        name: "undefined",
        src: this.default_src,
        age: -1,
        key: 0
      };
      return;
    },
    // estimate age for a single image (the current selected)
    estimate_age() {
      if (this.selected.age >= 0) return;
      let selected = this.selected;
      const config = { headers: { "Content-Type": "multipart/form-data" } };
      const data = new FormData();
      data.append("image_url", selected.src);
      axios.post("http://localhost:8081/estimate_age", data, config)
        .then(response => {
          selected.age = response.data.age;
        });
    },
    // estimate age for all images that don't have a defined apparent age
    estimate_age_all() {
      this.working = true;
      let unestimated = [];
      for (let i = 0; i < this.list.length; i++) {
        if (this.list[i].age < 0) {
          unestimated.push(this.list[i]);
        }
      }
      const config = { headers: { "Content-Type": "multipart/form-data" } };
      const data = new FormData();
      data.append("unestimated", JSON.stringify(unestimated));
      axios.post("http://localhost:8081/estimate_age_all", data, config)
        .then(response => {
          let results = response.data.results;
          for (let i = 0; i < results.length; i++) {
            for (let j = 0; j < unestimated.length; j++) {
              if (unestimated[j].key == results[i].key) {
                unestimated[j].age = results[i].age;
                break;
              }
            }
          }
          this.working = false;
        });
    },
    // sort images according to age (undefined ages are sorted to the back)
    sort_images() {
      this.list.sort(function(a, b) {
        if (a.age < 0 && b.age < 0) return 0;
        else if (a.age < 0) return 1;
        else if (b.age < 0) return -1;
        else return a.age - b.age;
      });
    },
    // render video!!!
    render_video() {
      this.working = true;
      const config = { headers: { "Content-Type": "multipart/form-data" } };
      const data = new FormData();
      data.append("list", JSON.stringify(this.list));
      data.append("mode", this.transition_type);
      data.append("pause", this.pause);
      data.append("fps", this.fps);
      if (this.transition_type == "cross-fading") {
        data.append("duration", this.fade_duration);
      }
      axios.post("http://localhost:8081/render_video", data, config)
        .then(response => {
          // Flask sends over video in raw bytes (with "charset=x-user-defined")
          // however all bytes > 127 are prefixed with 0xf7, e.g. df -> f7df (at least in Chrome)
          // we need to mask it off and then coerce the byte stream into a buffer
          // so that Blob will not do any more unwanted encoding/conversions
          let buffer = new ArrayBuffer(response.data.length);
          let ubyte8 = new Uint8Array(buffer);
          for (let i = 0; i < response.data.length; i++) {
            ubyte8[i] = response.data.charCodeAt(i); // leading bits are truncated when cast to uint8
          }
          let file = new File([buffer], "out_h264.mp4", {type: "video/mp4"});
          let video_url = URL.createObjectURL(file);
          this.video_view = true;
          this.video_src = video_url;
          this.working = false;
        })
    },
    // play the most recently rendered video on user command
    play_video() {
      if (this.video_src == undefined) return;
      this.video_view = true;
    },
    // download video via browser
    save_video() {
      if (this.video_src == undefined) return;
      let a = document.createElement("a");
      a.href = this.video_src;
      a.download = "out_h264.mp4";
      a.click();
    },
    // backdoor for developer
    __debug__() {
      console.log(this.list);
    }
  },
  created: function() {
    let __debug__ = this.__debug__;
    window.addEventListener("keydown", function(e) {
      if (e.keyCode == 68) __debug__(); // press D for debugging info
    });
  }
};
</script>

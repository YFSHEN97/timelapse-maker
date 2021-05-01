<template>
  <v-app>
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
            @mousedown="selected=element"
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
      <v-btn dark block left class="py-0 mt-1">
        <v-icon left class="mr-2">mdi-face-recognition</v-icon>
        <span>Estimate Age for Selected</span>
      </v-btn>
      <!-- Button for estimating age for all undefined -->
      <v-btn dark block left class="py-0 mt-1">
        <v-icon left class="mr-2">mdi-face-woman-shimmer-outline</v-icon>
        <span>Estimate Age for All</span>
      </v-btn>
      <!-- Button for sorting images by age -->
      <v-btn dark block left class="py-0 mt-1">
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

      <v-divider class="mt-4 mb-8" />
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
      <v-btn dark block left class="py-0 mt-1" :disabled="list.length < 2">
        <v-icon left class="mr-2">play_circle_outline</v-icon>
        <span>Render Video</span>
      </v-btn>
    </v-container>
    </v-navigation-drawer>

    <!-- Middle section for displaying selected image -->
    <v-main>
      <v-container>
        <v-row class="text-center">
          <v-col cols="12"><v-img :src="selected.src" contain height="550"/></v-col>
          <v-col><h2>Apparent age: {{ (selected.age == -1) ? "N/A" : String(selected.age) + " years" }}</h2></v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import draggable from 'vuedraggable'

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
      drag: false
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

import React from "react";

import GridQueue from "./GridQueue";

var lastX, lastY;
var isMouseDown = false;

const GRID_SIZE = 128;

export default class Canvas extends React.Component {
  constructor(props){
    super(props);
    this.x = 0;
    this.y = 0;
    this.size = 0;
    this.zoomIn = 1;
    this.grids = {}
    this.gridLoading = new GridQueue(this);
    this.gridLoading.work();

    this.mouseMove = this.mouseMove.bind(this);
    this.mouseDown = this.mouseDown.bind(this);
    this.mouseUp = this.mouseUp.bind(this);
    this.wheel = this.wheel.bind(this);
  }
  move(additionalX, additionalY) {
    this.x -= additionalX;
    this.y -= additionalY;
  }
  mouseMove(evt) {
    if(isMouseDown){
      evt.persist();
      var curX = evt.clientX;
      var curY = evt.clientY;
      this.move(curX - lastX, curY - lastY);
      lastY = curY;
      lastX = curX;
      this.forceUpdate()
    }
  }
  mouseDown(evt) {
    isMouseDown = true;
    lastX = evt.clientX;
    lastY = evt.clientY;
  }
  mouseUp(evt) {
    isMouseDown = false;
  }
  mouseClick(evt) {
  }

  wheel(evt) {
    evt.persist();
    if (evt.deltaY > 0)
    {
      if (this.zoomIn == 1) {
        if (this.size < 9)
          this.size = this.size + 1
      }
      else
        this.zoomIn /= 2;
    }
    if (evt.deltaY < 0)
    {
      if (this.size > 0)
         this.size = this.size - 1
      else {
        this.zoomIn *= 2;
      }
    }
  }
  render() {
    return (
      <canvas ref='canvas' width={window.innerWidth} height={window.innerHeight} onMouseMove={this.mouseMove}
      onMouseDown={this.mouseDown}
      onMouseUp={this.mouseUp}
      onWheel={this.wheel}>
      </canvas>
    );
  }
  async componentDidMount() {
    this.gridData = await fetch(get_grid_size_url);
    this.gridData = await this.gridData.json();
    this.gridData = JSON.parse(this.gridData);
    for (var i = 0; i < 10; i++) {
      var data = this.gridData[i];
      this.grids[i] = Array(this.gridData);
      for (var j = 0; j < data[0]; j++)
        this.grids[i][j] = Array(data[1]);
    }
    this.forceUpdate();
  }
  componentDidUpdate() {
    var cvx = this.refs.canvas.getContext("2d");
    var screenWidth = window.innerWidth;
    var screenHeight = window.innerHeight;

    var x = this.x;
    var y = this.y;

    var firstGridX = Math.floor(x / 128);
    var firstGridY = Math.floor(y / 128);
    var lastGridX = firstGridX + Math.ceil(screenWidth / (128 * this.zoomIn));
    var lastGridY = firstGridY + Math.ceil(screenHeight / (128 * this.zoomIn));
    if (firstGridX < 0)
      firstGridX = 0;
    if (firstGridY < 0)
      firstGridY = 0;
    if (lastGridX >= this.gridData[this.size][0])
      lastGridX = this.gridData[this.size][0] - 1
    if (lastGridY >= this.gridData[this.size][1])
      lastGridY = this.gridData[this.size][1] - 1
    cvx.fillColor = "black";
    cvx.transform(1, 0, 0, 1, 0, 0);
    cvx.fillRect(0, 0, screenWidth, screenHeight);
    cvx.imageSmoothingEnabled = false;

    for (var i = firstGridX; i <= lastGridX; i += 1)
      for (var j = firstGridY; j <= lastGridY; j += 1)
        if (this.grids[this.size][i][j] == null)
          this.gridLoading.append(i, j, this.size);
        else {
          var cur_rect = this.grids[this.size][i][j];
          drawPic(cur_rect, cvx, i * GRID_SIZE - x,j * GRID_SIZE - y);
    }
    cvx.drawImage(this.refs.canvas, 0, 0, screenWidth / this.zoomIn, screenHeight / this.zoomIn,
     0, 0, screenWidth, screenHeight);

  }
}

function drawPic(array, ctx, x_coord, y_coord) {
  var width = array.length,
    height = array[0].length,
    buffer = new Uint8ClampedArray(width * height * 4);

  for(var y = 0; y < height; y++) {
    for(var x = 0; x < width; x++) {
      var p = width * y * 4   + x * 4;
      buffer[p+0] = array[x][y][0];
      buffer[p+1] = array[x][y][1];
      buffer[p+2] = array[x][y][2];
      buffer[p+3] = 255;
    }
  }
  var idata = ctx.createImageData(width, height);

  // set our buffer as source
  idata.data.set(buffer);

  // update canvas with new data
  ctx.putImageData(idata, x_coord, y_coord);
}

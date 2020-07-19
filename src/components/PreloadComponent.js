import React from "react";

export default class PreloadComponent extends React.Component {
  constructor (props) {
    super(props);
    this.state = {mounted: true};
  }
  render () {
    if (this.state.mounted)
      return (
        <div class='preload'>
          <div class='preloadText'>
            LOADING, PLEASE WAIT
          </div>
        </div>
      )
    else
      return null;
  }
}
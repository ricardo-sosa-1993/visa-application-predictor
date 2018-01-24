import { Component } from "@angular/core";
import { FormControl, FormGroupDirective, NgForm } from "@angular/forms";
import { ValueTransformer } from "@angular/compiler/src/util";
import { ErrorStateMatcher } from "@angular/material/core";
import { OnInit } from "@angular/core/src/metadata/lifecycle_hooks";

export class ParentErrorStateMatcher implements ErrorStateMatcher {
  isErrorState(
    control: FormControl | null,
    form: FormGroupDirective | NgForm | null
  ): boolean {
    const isSubmitted = !!(form && form.submitted);
    const controlTouched = !!(control && (control.dirty || control.touched));
    const controlInvalid = !!(control && control.invalid);
    const parentInvalid = !!(
      control &&
      control.parent &&
      control.parent.invalid &&
      (control.parent.dirty || control.parent.touched)
    );

    return isSubmitted || (controlTouched && (controlInvalid || parentInvalid));
  }
}

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.css"]
})
export class AppComponent implements OnInit {
  title = "Visa Predictor";
  accuracy = null;
  result = null;
  columns = {
    class_of_admission: {
      control: new FormControl(),
      options: [],
      filteredOptions: [],
      selectedOption: null
    },
    country_of_citizenship: {
      control: new FormControl(),
      options: [],
      filteredOptions: [],
      selectedOption: null
    },
    foreign_worker_info_education: {
      control: new FormControl(),
      options: [],
      filteredOptions: [],
      selectedOption: null
    },
    foreign_worker_info_major: {
      control: new FormControl(),
      options: [],
      filteredOptions: [],
      selectedOption: null
    },
    job_info_work_state: {
      control: new FormControl(),
      options: [],
      filteredOptions: [],
      selectedOption: null
    },
    pw_soc_title: {
      control: new FormControl(),
      options: [],
      filteredOptions: [],
      selectedOption: null,
    }
  };
  error = false;
  parentErrorStateMatcher = new ParentErrorStateMatcher();

  onSubmit = () => {
    const invalidFields = Object.keys(this.columns).find(
      key => !this.columns[key].control.valid
    );
    // All fields are valid
    if (!invalidFields) {
      const request = Object.keys(this.columns).reduce((prevValue, key) => {
        prevValue[key] = this.columns[key].selectedOption;
        return prevValue;
      }, {});
      // Request prediction
      fetch('http://127.0.0.1:8000/predict/', {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        method: "POST",
        body: JSON.stringify(request)
      }).then(response => response.json()).then(prediction => {
        this.result = prediction[0];
      });
    }
  };

  getValueSetter = field => {
    return value => {
      if (value) {
        this.result = null;
        const lowerCaseValue = value.trim().toLowerCase();
        this.columns[field].filteredOptions = this.columns[field].options
          .filter(option => option.toLowerCase().includes(lowerCaseValue))
          .slice(0, 5);
        // The entered value is the same as the first option
        if (
          this.columns[field].filteredOptions.length &&
          lowerCaseValue ===
            this.columns[field].filteredOptions[0].trim().toLowerCase()
        ) {
          this.columns[field].selectedOption = this.columns[
            field
          ].filteredOptions[0];
          this.columns[field].control.setErrors(null);
        } else {
          this.columns[field].control.setErrors({ incorrect: true });
        }
      } else {
        this.columns[field].filteredOptions = [];
      }
    };
  };

  ngOnInit() {
    // Get options
    fetch("http://127.0.0.1:8000/options/")
      .then(response => response.json())
      .then(async data => {
        const jsonData = JSON.parse(data);
        Object.keys(jsonData).forEach(key => {
          this.columns[key].options = jsonData[key];
          this.columns[key].filteredOptions = [];
          this.columns[key].selectedOption = null;
        });
      });
    // Get accuracy
    fetch("http://127.0.0.1:8000/accuracy/")
      .then(response => response.json())
      .then(accuracy => {
        this.accuracy = `${(parseFloat(accuracy) * 100).toFixed(2)}%`;
      });
    // Add change listeners
    Object.keys(this.columns).forEach(key =>
      this.columns[key].control.valueChanges.subscribe(this.getValueSetter(key))
    );
  }
}

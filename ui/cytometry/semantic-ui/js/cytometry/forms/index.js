import { DepositFormApp, parseFormAppConfig, EDTFSingleDatePicker } from "@js/oarepo_ui/forms";
import { RDMCompleteSections } from "@js/oarepo_rdm/form";
import React from "react";
import ReactDOM from "react-dom";
import { parametrize } from "react-overridable";
import { ProjectInfoSection } from "./ProjectInfoSection";
import { SampleProvenanceSection } from "./SampleProvenanceSection";
import { PreparationSection } from "./PreparationSection";
import { InstrumentationSection } from "./InstrumentationSection";
import { MeasurementSection } from "./MeasurementSection";

const parametrizeEDTFSingleDatePicker = parametrize(EDTFSingleDatePicker, {
  customInputProps: { width: 16 },
});

const { rootEl, config, ...rest } = parseFormAppConfig();

const componentOverrides = {
  "InvenioRdmRecords.DepositForm.DatesField.DateField":
    parametrizeEDTFSingleDatePicker,
};

const sections = [
  ...RDMCompleteSections,
  ProjectInfoSection,
  SampleProvenanceSection,
  PreparationSection,
  InstrumentationSection,
  MeasurementSection,
];

ReactDOM.render(
  <DepositFormApp
    config={config}
    {...rest}
    sections={sections}
    componentOverrides={componentOverrides}
    useWizardForm
  />,
  rootEl,
);

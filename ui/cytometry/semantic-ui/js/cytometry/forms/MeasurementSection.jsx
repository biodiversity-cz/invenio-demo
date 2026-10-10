import React from "react";
import { TextField } from "@js/oarepo_ui/forms";
import { i18next } from "@translations/i18next";
import { MeasurerNameField } from "./MeasurerNameField";

const MeasurementFields = () => (
  <>
    <MeasurerNameField />
    <TextField
      fieldPath="metadata.measurement.measurement_date"
      label={i18next.t("Measurement date")}
      placeholder="YYYY, YYYY-MM, or YYYY-MM-DD"
    />
    <TextField
      fieldPath="metadata.measurement.purpose"
      label={i18next.t("Purpose")}
      optimized
    />
    <TextField
      fieldPath="metadata.measurement.peakSampleToPeakStandard"
      label={i18next.t("Sample peak / standard peak")}
    />
    <TextField
      fieldPath="metadata.measurement.interpretation_notes"
      label={i18next.t("Interpretation notes")}
      optimized
    />
  </>
);

export const MeasurementSection = {
  key: "measurement",
  label: i18next.t("Measurement"),
  component: MeasurementFields,
  includesPaths: [
    "metadata.measurement.measurer_name",
    "metadata.measurement.measurement_date",
    "metadata.measurement.purpose",
    "metadata.measurement.peakSampleToPeakStandard",
    "metadata.measurement.interpretation_notes",
  ],
};

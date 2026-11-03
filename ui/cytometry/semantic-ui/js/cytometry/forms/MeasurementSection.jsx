import React from "react";
import { TextField } from "@js/oarepo_ui/forms";
import { FieldLabel } from "react-invenio-forms";
import { useFormikContext, getIn, FieldArray } from "formik";
import { Form, Icon, Button, Checkbox } from "semantic-ui-react";
import { i18next } from "@translations/i18next";

const PEAKS_FIELD_PATH = "metadata.measurement.sample_peaks";

function SamplePeaksField() {
  const { values } = useFormikContext();

  return (
    <Form.Field required>
      <FieldLabel htmlFor={PEAKS_FIELD_PATH} label={i18next.t("Sample peaks")} />
      <FieldArray
        name={PEAKS_FIELD_PATH}
        render={(arrayHelpers) => {
          const peaks = getIn(values, PEAKS_FIELD_PATH, []);
          return (
            <>
              {peaks.map((item, index) => {
                const base = `${PEAKS_FIELD_PATH}.${index}`;
                const isLast = index === peaks.length - 1;
                return (
                  <div
                    // eslint-disable-next-line react/no-array-index-key
                    key={index}
                    className="sample-peak-array-entry"
                  >
                    <TextField
                      fieldPath={`${base}.peak_position`}
                      label={i18next.t("Peak position")}
                      required
                      width={16}
                    />
                    <TextField
                      fieldPath={`${base}.peak_sample_to_peak_standard`}
                      label={i18next.t("Sample peak / standard peak")}
                      width={16}
                    />
                    <TextField
                      fieldPath={`${base}.peak_description`}
                      label={i18next.t("Peak description")}
                      width={16}
                    />
                    <Form.Field>
                      <Button.Group>
                        <Button
                          aria-label={i18next.t("Remove peak")}
                          className="close-btn"
                          type="button"
                          icon
                          labelPosition="left"
                          onClick={() => arrayHelpers.remove(index)}
                        >
                          <Icon name="close" />
                          {i18next.t("Remove peak")}
                        </Button>
                        {isLast ? (
                          <Button
                            className="array-field-add-button"
                            type="button"
                            icon
                            labelPosition="left"
                            onClick={() => arrayHelpers.push({})}
                          >
                            <Icon name="add" />
                            {i18next.t("Add peak")}
                          </Button>
                        ) : null}
                      </Button.Group>
                    </Form.Field>
                  </div>
                );
              })}
              {peaks.length === 0 ? (
                <Form.Button
                  className="array-field-add-button inline"
                  type="button"
                  icon
                  labelPosition="left"
                  onClick={() => arrayHelpers.push({})}
                >
                  <Icon name="add" />
                  {i18next.t("Add peak")}
                </Form.Button>
              ) : null}
            </>
          );
        }}
      />
    </Form.Field>
  );
}

function InternalStandardUsedField() {
  const { values, setFieldValue } = useFormikContext();
  const path = "metadata.measurement.internal_standard_used";
  const checked = Boolean(getIn(values, path, true));

  return (
    <Form.Field required>
      <Checkbox
        label={i18next.t("Internal standard used")}
        checked={checked}
        onChange={(_e, data) => setFieldValue(path, Boolean(data.checked))}
      />
    </Form.Field>
  );
}

const MeasurementFields = () => (
  <>
    <TextField
      fieldPath="metadata.measurement.measurer.fullname"
      label={i18next.t("Measurer full name")}
    />
    <TextField
      fieldPath="metadata.measurement.measurer.orcid"
      label={i18next.t("Measurer ORCID")}
    />
    <TextField
      fieldPath="metadata.measurement.measurer.affiliation"
      label={i18next.t("Measurer affiliation")}
    />
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
    <InternalStandardUsedField />
    <TextField
      fieldPath="metadata.measurement.standard_peak_position"
      label={i18next.t("Standard peak position")}
    />
    <SamplePeaksField />
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
    "metadata.measurement.measurer",
    "metadata.measurement.measurement_date",
    "metadata.measurement.purpose",
    "metadata.measurement.internal_standard_used",
    "metadata.measurement.standard_peak_position",
    "metadata.measurement.sample_peaks",
    "metadata.measurement.interpretation_notes",
  ],
};

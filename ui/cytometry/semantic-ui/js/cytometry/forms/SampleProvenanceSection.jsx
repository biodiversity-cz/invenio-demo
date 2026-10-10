import React from "react";
import { TextField, StringArrayField } from "@js/oarepo_ui/forms";
import { FieldLabel } from "react-invenio-forms";
import { useFormikContext, getIn, FieldArray } from "formik";
import { Form, Icon, Button } from "semantic-ui-react";
import { i18next } from "@translations/i18next";

const TAXON_FIELD_PATH = "metadata.sample_provenance.taxon";

function TaxonArrayField() {
  const { values } = useFormikContext();

  return (
    <Form.Field>
      <FieldLabel htmlFor={TAXON_FIELD_PATH} label={i18next.t("Taxa")} />
      <FieldArray
        name={TAXON_FIELD_PATH}
        render={(arrayHelpers) => {
          const taxa = getIn(values, TAXON_FIELD_PATH, []);
          return (
            <>
              {taxa.map((item, index) => {
                const base = `${TAXON_FIELD_PATH}.${index}`;
                const isLast = index === taxa.length - 1;
                return (
                  <div
                    // eslint-disable-next-line react/no-array-index-key
                    key={index}
                    className="taxon-array-entry"
                  >
                    <TextField
                      fieldPath={`${base}.scientific_name`}
                      label={i18next.t("Scientific name")}
                      required
                      width={16}
                    />
                    <TextField
                      fieldPath={`${base}.strain_cultivar`}
                      label={i18next.t("Strain / cultivar")}
                      width={16}
                    />
                    <TextField
                      fieldPath={`${base}.col_id`}
                      label={i18next.t("Catalogue of Life ID")}
                      width={16}
                    />
                    <TextField
                      fieldPath={`${base}.notes`}
                      label={i18next.t("Taxon notes")}
                      optimized
                      width={16}
                    />
                    <Form.Field>
                      <Button.Group>
                        <Button
                          aria-label={i18next.t("Remove field")}
                          className="close-btn"
                          type="button"
                          icon
                          labelPosition="left"
                          onClick={() => arrayHelpers.remove(index)}
                        >
                          <Icon name="close" />
                          {i18next.t("Remove taxon")}
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
                            {i18next.t("Add taxon")}
                          </Button>
                        ) : null}
                      </Button.Group>
                    </Form.Field>
                  </div>
                );
              })}
              {taxa.length === 0 ? (
                <Form.Button
                  className="array-field-add-button inline"
                  type="button"
                  icon
                  labelPosition="left"
                  onClick={() => arrayHelpers.push({})}
                >
                  <Icon name="add" />
                  {i18next.t("Add taxon")}
                </Form.Button>
              ) : null}
            </>
          );
        }}
      />
    </Form.Field>
  );
}

export const SampleProvenanceSection = {
  key: "sample_provenance",
  label: i18next.t("Sample provenance"),
  component: () => (
    <>
      <TaxonArrayField />
      <TextField
        fieldPath="metadata.sample_provenance.location.country_or_region"
        label={i18next.t("Country or region")}
      />
      <TextField
        fieldPath="metadata.sample_provenance.location.locality_description"
        label={i18next.t("Locality description")}
        optimized
      />
      <TextField
        fieldPath="metadata.sample_provenance.location.coordinates"
        label={i18next.t("Coordinates")}
      />
      <TextField
        fieldPath="metadata.sample_provenance.date_of_sampling"
        label={i18next.t("Date of sampling")}
        placeholder="YYYY, YYYY-MM, or YYYY-MM-DD"
      />
      <StringArrayField
        fieldPath="metadata.sample_provenance.collector"
        label={i18next.t("Collector(s)")}
        addButtonLabel={i18next.t("Add collector")}
      />
      <TextField
        fieldPath="metadata.sample_provenance.collection_id"
        label={i18next.t("Collection ID")}
      />
      <TextField
        fieldPath="metadata.sample_provenance.voucher"
        label={i18next.t("Voucher")}
      />
      <TextField
        fieldPath="metadata.sample_provenance.material_entity"
        label={i18next.t("Material entity")}
      />
      <TextField
        fieldPath="metadata.sample_provenance.specimen_id"
        label={i18next.t("Specimen ID")}
      />
    </>
  ),
  includesPaths: [
    "metadata.sample_provenance.taxon",
    "metadata.sample_provenance.location",
    "metadata.sample_provenance.date_of_sampling",
    "metadata.sample_provenance.collector",
    "metadata.sample_provenance.collection_id",
    "metadata.sample_provenance.voucher",
    "metadata.sample_provenance.material_entity",
    "metadata.sample_provenance.specimen_id",
  ],
};

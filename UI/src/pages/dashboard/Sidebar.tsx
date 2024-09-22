import { useState, useCallback, useEffect } from "react";
import { Button, Paper, Stack, TextField, Typography } from "@mui/material";
import type { Charge, Email, FetchDataResponse } from "@/app/slices/types";
import Loading from "@/components/Loading";

type Props = {
  data: FetchDataResponse;
  dataStatus: string;
  emails: Email[];
  emailIndex: number;
  changeEmailIndex: (newIndex: number) => void;
  skipForManualReview: () => void;
  saveForCWUpload: (debit_note_data: FetchDataResponse) => void;
};

function Sidebar({
  data,
  dataStatus,
  emails,
  emailIndex,
  changeEmailIndex,
  skipForManualReview,
  saveForCWUpload,
}: Props) {
  const [debitNoteData, setDebitNoteData] = useState<FetchDataResponse>({});

  useEffect(() => {
    setDebitNoteData(data);
  }, [data]);

  const getChargeUSD = useCallback(
    (charge_code: string) => {
      const charge = debitNoteData.charges?.find(
        (charge) => charge.charge_code === charge_code
      );
      return charge?.charges_in_usd ? charge?.charges_in_usd : "";
    },
    [debitNoteData]
  );

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;

    setDebitNoteData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  }, []);

  const handleChargeChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const { name, value } = e.target;
      const { charges } = debitNoteData;
      let newCharges: Charge[];

      if (charges?.find((charge) => charge.charge_code === name)) {
        newCharges = charges?.map((charge) => {
          if (charge.charge_code === name) {
            return {
              ...charge,
              charges_in_usd: parseFloat(value),
            };
          }
          return charge;
        });
      } else {
        const newCharge = {
          id: null,
          charge_code: name,
          charges_in_usd: parseFloat(value),
          description: "",
        };
        newCharges = charges ? [...charges, newCharge] : [newCharge];
      }

      setDebitNoteData((prevData) => ({
        ...prevData,
        charges: newCharges,
      }));
    },
    [debitNoteData]
  );

  const getTotalCharges = useCallback(() => {
    const charges = debitNoteData.charges;
    const totalCharges = charges?.reduce(
      (sum, charge) => sum + (Number(charge.charges_in_usd) || 0),
      0
    );
    return totalCharges;
  }, [debitNoteData]);

  return (
    <Stack spacing={2}>
      <Paper
        elevation={5}
        sx={{ bgcolor: "#F1A22C", padding: 2, minHeight: "150px" }}
      >
        <Stack spacing={1}>
          <Stack direction="row" spacing={1}>
            <Typography variant="h5" color="#222C68">
              Email:
            </Typography>
            <Typography variant="h5" color="#222C68">
              {`${emailIndex + 1} / ${emails.length}`}
            </Typography>
          </Stack>
          <Stack direction="row" spacing={1}>
            <Typography variant="h5" color="#222C68">
              Total Charges:
            </Typography>
            <Typography
              variant="h5"
              color="#222C68"
              sx={{ fontWeight: "bold" }}
            >
              {getTotalCharges()}
            </Typography>
          </Stack>
          <Stack direction="row" spacing={1}>
            <Typography variant="button" color="#222C68">
              {debitNoteData.subject}
            </Typography>
          </Stack>
        </Stack>
      </Paper>
      <Stack direction="row" spacing={1}>
        <Button
          color="info"
          disabled={emailIndex === 0 ? true : false}
          onClick={() => changeEmailIndex(emailIndex - 1)}
          variant="contained"
          sx={{ flexBasis: 0, flexGrow: 1 }}
        >
          Go to Previous Invoice
        </Button>
        <Button
          color="info"
          disabled={emailIndex === emails.length - 1 ? true : false}
          onClick={() => changeEmailIndex(emailIndex + 1)}
          variant="contained"
          sx={{ flexBasis: 0, flexGrow: 1 }}
        >
          Go to Next Invoice
        </Button>
      </Stack>
      {dataStatus === "succeeded" ? (
        <>
          <Stack direction="row" spacing={1}>
            <TextField
              label="SHIPMENT ID"
              name="agl_shipment_number"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              value={debitNoteData.agl_shipment_number || ""}
              onChange={handleChange}
            />
          </Stack>
          <Stack direction="row" spacing={1}>
            <TextField
              label="Email ID"
              name="email_id"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              value={debitNoteData.email_id || ""}
            />
          </Stack>
          <Stack direction="row" spacing={1}>
            <TextField
              label="Creditor"
              name="creditor"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              value={debitNoteData.creditor || ""}
              onChange={handleChange}
            />
            <TextField
              label="Invoice Num"
              name="invoice_num"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              value={debitNoteData.invoice_num || ""}
              onChange={handleChange}
            />
          </Stack>
          <Stack direction="row" spacing={1}>
            <TextField
              label="Invoice Date"
              name="invoice_date"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              type="date"
              value={debitNoteData.invoice_date || ""}
              onChange={handleChange}
            />
            <TextField
              label="Supplier Cost Ref"
              name="supplier_cost_ref"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              value={debitNoteData.supplier_cost_ref || ""}
              onChange={handleChange}
            />
          </Stack>
          <Stack direction="row" spacing={1}>
            <TextField
              label="Is AR or AP"
              name="ar_ap"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              value={debitNoteData.ar_ap || ""}
              onChange={handleChange}
            />
            <TextField
              label="Is Post(Y/N)"
              name="is_post"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              value={debitNoteData.is_post || ""}
              onChange={handleChange}
            />
          </Stack>
          <Stack direction="row" spacing={1}>
            <TextField
              label="FRT"
              name="FRT"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              type="number"
              value={getChargeUSD("FRT")}
              onChange={handleChargeChange}
            />
            <TextField
              label="AGEN"
              name="AGEN"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              type="number"
              value={getChargeUSD("AGEN")}
              onChange={handleChargeChange}
            />
          </Stack>
          <Stack direction="row" spacing={1}>
            <TextField
              label="AMS"
              name="AMS"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              type="number"
              value={getChargeUSD("AMS")}
              onChange={handleChargeChange}
            />
            <TextField
              label="EQUIP"
              name="EQUIP"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              type="number"
              value={getChargeUSD("EQUIP")}
              onChange={handleChargeChange}
            />
          </Stack>
          <Stack direction="row" spacing={1}>
            <TextField
              label="ORIGIN"
              name="ORIGIN"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              type="number"
              value={getChargeUSD("ORIGIN")}
              onChange={handleChargeChange}
            />
            <TextField
              label="LOCAL"
              name="LOCAL"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              type="number"
              value={getChargeUSD("LOCAL")}
              onChange={handleChargeChange}
            />
          </Stack>
          <Stack direction="row" spacing={1}>
            <TextField
              label="PP"
              name="PP"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              type="number"
              value={getChargeUSD("PP")}
              onChange={handleChargeChange}
            />
            <TextField
              label="TERFEE"
              name="TERFEE"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              type="number"
              value={getChargeUSD("TERFEE")}
              onChange={handleChargeChange}
            />
          </Stack>
          <Stack direction="row" spacing={1}>
            <TextField
              label="TELEX"
              name="TELEX"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              type="number"
              value={getChargeUSD("TELEX")}
              onChange={handleChargeChange}
            />
            <TextField
              label="VGM"
              name="VGM"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              type="number"
              value={getChargeUSD("VGM")}
              onChange={handleChargeChange}
            />
          </Stack>
          <Stack direction="row" spacing={1}>
            <TextField
              label="DCART"
              name="DCART"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              type="number"
              value={getChargeUSD("DCART")}
              onChange={handleChargeChange}
            />
            <TextField
              label="SEAL"
              name="SEAL"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              type="number"
              value={getChargeUSD("SEAL")}
              onChange={handleChargeChange}
            />
          </Stack>
          <Stack direction="row" spacing={1}>
            <TextField
              label="DOC"
              name="DOC"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              type="number"
              value={getChargeUSD("DOC")}
              onChange={handleChargeChange}
            />
            <TextField
              label="BOOK"
              name="BOOK"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              type="number"
              value={getChargeUSD("BOOK")}
              onChange={handleChargeChange}
            />
          </Stack>
          <Stack direction="row" spacing={1}>
            <TextField
              label="CCLR"
              name="CCLR"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              type="number"
              value={getChargeUSD("CCLR")}
              onChange={handleChargeChange}
            />
            <TextField
              label="ALINE"
              name="ALINE"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              type="number"
              value={getChargeUSD("ALINE")}
              onChange={handleChargeChange}
            />
          </Stack>
          <Stack direction="row" spacing={1}>
            <TextField
              label="PSEC"
              name="PSEC"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              type="number"
              value={getChargeUSD("PSEC")}
              onChange={handleChargeChange}
            />
            <TextField
              label="EGF"
              name="EGF"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              type="number"
              value={getChargeUSD("EGF")}
              onChange={handleChargeChange}
            />
          </Stack>
          <Stack direction="row" spacing={1}>
            <TextField
              label="TRANS"
              name="TRANS"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              type="number"
              value={getChargeUSD("TRANS")}
              onChange={handleChargeChange}
            />
            <TextField
              label="CHRENT"
              name="CHRENT"
              size="small"
              sx={{ flexBasis: 0, flexGrow: 1 }}
              type="number"
              value={getChargeUSD("CHRENT")}
              onChange={handleChargeChange}
            />
          </Stack>
        </>
      ) : (
        <Loading />
      )}
      <Button
        color="success"
        variant="contained"
        onClick={() => saveForCWUpload(debitNoteData)}
      >
        Save Data for CW Upload
      </Button>
      <Button color="error" variant="outlined" onClick={skipForManualReview}>
        Skip for Manual Review
      </Button>
    </Stack>
  );
}

export default Sidebar;

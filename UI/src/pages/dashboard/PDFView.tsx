import { useCallback, useState } from "react";
import {
  ButtonGroup,
  IconButton,
  Pagination,
  Stack,
  Typography,
} from "@mui/material";
import {
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
} from "@mui/icons-material";
import { useResizeObserver } from "@wojtekmaj/react-hooks";
import { pdfjs, Document, Page } from "react-pdf";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";
import "react-pdf/dist/esm/Page/TextLayer.css";
import type { PDFDocumentProxy } from "pdfjs-dist";
// component
import Loading from "@/components/Loading";

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.mjs",
  import.meta.url
).toString();

const options = {
  cMapUrl: "/cmaps/",
  standardFontDataUrl: "/standard_fonts/",
};

const resizeObserverOptions = {};

type Props = {
  pdfUrl: string | null;
  pdfStatus: string;
  pdfError: string | null;
};

function PDFView({ pdfUrl, pdfStatus, pdfError }: Props) {
  const [numPages, setNumPages] = useState<number>();
  const [page, setPage] = useState<number>(1);
  const [containerRef, setContainerRef] = useState<HTMLElement | null>(null);
  const [containerWidth, setContainerWidth] = useState<number>();
  const [maxWidth, setMaxWidth] = useState<number>(1000);

  const onResize = useCallback<ResizeObserverCallback>((entries) => {
    const [entry] = entries;

    if (entry) {
      setContainerWidth(entry.contentRect.width);
    }
  }, []);

  useResizeObserver(containerRef, resizeObserverOptions, onResize);

  function onDocumentLoadSuccess({
    numPages: nextNumPages,
  }: PDFDocumentProxy): void {
    setNumPages(nextNumPages);
  }

  const handleChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  return (
    <div className="pdf-viewer">
      <div className="pdf-viewer__container">
        <div className="pdf-viewer__container__document" ref={setContainerRef}>
          {pdfStatus === "succeeded" && pdfUrl && (
            <Stack justifyContent="center">
              <Document
                file={pdfUrl}
                onLoadSuccess={onDocumentLoadSuccess}
                options={options}
              >
                <Page
                  pageNumber={page}
                  width={
                    containerWidth
                      ? Math.min(containerWidth, maxWidth)
                      : maxWidth
                  }
                />
              </Document>
              <Stack
                direction="row"
                justifyContent="space-around"
                alignItems="center"
              >
                <ButtonGroup aria-label="zoom button group">
                  <IconButton
                    onClick={() => setMaxWidth(maxWidth + 50)}
                    disabled={maxWidth >= 1100 ? true : false}
                    color="primary"
                    aria-label="zoom in button"
                  >
                    <ZoomInIcon />
                  </IconButton>
                  <IconButton
                    onClick={() => setMaxWidth(maxWidth - 50)}
                    disabled={maxWidth <= 800 ? true : false}
                    color="primary"
                    aria-label="zoom out button"
                  >
                    <ZoomOutIcon />
                  </IconButton>
                </ButtonGroup>
                <Pagination
                  count={numPages}
                  page={page}
                  color="primary"
                  shape="rounded"
                  onChange={handleChange}
                />
              </Stack>
            </Stack>
          )}
          {pdfStatus === "loading" && <Loading />}
          {pdfStatus === "failed" && (
            <Typography variant="h5">Error: {pdfError}</Typography>
          )}
        </div>
      </div>
    </div>
  );
}

export default PDFView;

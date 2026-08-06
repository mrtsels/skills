# Chinese Fund Valuation Sheet Extraction

Patterns for extracting fund manager info from Chinese private fund valuation sheets (估值表).

## File Format Detection

| Extension | Library | When it fails |
|-----------|---------|--------------|
| .pdf | `fitz` (PyMuPDF) | Scanned PDFs (images instead of text) |
| .xlsx | `openpyxl` | Some TA exports have only 1 data row |
| .xls | `xlrd` | Same as xlsx for older format |

## Where the Manager Name Lives

In Chinese fund valuation sheets, the fund manager (管理人) name appears in:

1. **PDF table header line** — Format: `托管人_基金名称_专用表` or `管理人_基金名称_专用表`
   - Example: `华泰证券股份有限公司__千衍六维1号私募证券投资基金__专用表` (华泰 = custodian, not manager)
   - Example: `上海久期量和投资有限公司_久期量和灵活策略1号私募证券投资基金_专用表` (上海久期量和 = manager)
   - The fund manager is the entity before the first underscore when the format is `管理人_产品名_专用表`

2. **PDF header image** — Some PDFs have the header as an embedded image (4x 600x600 PNG stamps per page). Extract with:
   ```python
   images = page.get_images(full=True)
   for i, img in enumerate(images):
       base = doc.extract_image(img[0])
       # save and use vision_analyze
   ```

3. **Rendered page image** — When text extraction misses the header entirely, render the full page:
   ```python
   pix = page.get_pixmap(dpi=200)
   pix.save("page0.png")
   # Then use vision_analyze on the PNG
   ```

## Custodian vs Manager

The header `华泰证券股份有限公司__翔云50私募证券投资基金__专用表` means 华泰证券 is the **custodian** (托管人), not the manager. The manager must be found from:
- The fund product name (品牌 prefix, e.g. "翔云" → 广州翔云私募基金管理有限公司)
- The AMAC (基金业协会) registration lookup
- Third-party sources (天天基金网, 私募排排网)

## Verification Steps

1. Extract text from all available files (PDF text layer)
2. For scanned headers: render + vision_analyze
3. For xlsx/xls: check if it's a TA data export (minimal rows, no header)
4. Cross-reference fund product names with web search (百度/天天基金网)
5. For AMAC registration, check: 管理人公示 page for 备案编号, 登记时间

## Common Patterns

- Fund product name prefix = manager brand name (e.g. "千衍XX号" → 千衍私募基金管理)
- Some managers have "广州" or "深圳" or "上海" prefix in their legal name matching their registration city
- xlsx TA exports show the FOF trust name in column J (TA账号名称), not the underlying fund manager

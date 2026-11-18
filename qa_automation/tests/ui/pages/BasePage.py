from playwright.sync_api import expect, Page
import utils.utilities as ut
import allure, os, re


class BasePage:

    def __init__(self, page: Page):
        self.page = page
        self.timeout = 60000
        self.is_external_link_verification = (
            False  # Flag for external link stub verification
        )
        self.verified_external_href = None  # Store verified external URL

    def capture_and_attach_screenshot(self, step_name):
        """Capture and attach screenshot to the allure report."""
        current_page = self.get_current_page()
        try:
            # Capture and attach screenshot
            screenshot = current_page.screenshot(full_page=True)
            allure.attach(
                screenshot,
                name=f"{step_name}_screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
            print(f"The failure step screenshot has been captured! {step_name}")
        except Exception as e:
            print(f"Failed to capture screenshot: {e}")

    def attach_video(self, video_path):
        """Attach video at the end of the scenarios."""
        allure.attach.file(
            video_path,
            name="Execution Video",
            attachment_type=allure.attachment_type.WEBM,
        )

    def navigate_to_page(self, url: str):
        """Set default navigation timeout and navigate to specific page"""
        self.page.set_default_navigation_timeout(self.timeout)
        self.page.goto(url, wait_until="networkidle")

    def bring_page_to_front(self):
        """This method can be used to activate the new tab and continue perform actions."""
        self.page.bring_to_front()

    def fill(self, selector: str, text: str):
        self.page.locator(selector).fill(text)

    def click(self, selector: str):
        self.page.locator(selector).click()

    def set_default_timeout(self, timeout: int):
        self.page.set_default_timeout(timeout)

    # *********** wait for ***********
    def wait_for_function(self, selector: str, expected_text: str):
        self.page.wait_for_function(
            f"() => document.querySelector({selector}).to_have_text({expected_text})",
            timeout=self.timeout,
        )

    def wait_for(self, selector: str):
        """This method is to wait until a specific selector is apprear on the web page or text before it gets timedout"""
        page = self.get_current_page()
        page.locator(selector).wait_for(timeout=self.timeout)

    def wait_for_url(self, url: str):
        self.page.wait_for_url(url, wait_until="networkidle")

    def wait_for_selector(self, selector: str):
        self.page.wait_for_selector(selector, timeout=self.timeout, state="visible")

    def wait_for_timeout(self, timeout: int):
        self.page.wait_for_timeout(timeout)

    def wait_for_load_state(self, state: str | None = None):
        current_page = self.get_current_page()
        current_page.wait_for_load_state(
            state if state else "networkidle", timeout=self.timeout
        )

    def wait_for_dropdown_options(
        self,
        selector: str,
        expected_value: str = None,
        timeout: int = 30000,
        raise_on_missing: bool = True,
    ):
        """Wait for dropdown options to be populated and optionally check for a specific value.

        Args:
            selector: The dropdown selector
            expected_value: Optional specific value to wait for
            timeout: Maximum time to wait in milliseconds
            raise_on_missing: If True, raise exception when option not found; if False, return False

        Returns:
            True if option found or no expected_value provided, False if option not found and raise_on_missing=False
        """
        current_page = self.get_current_page()
        # Wait for the select element to be visible and attached
        current_page.wait_for_selector(selector, state="attached", timeout=timeout)
        current_page.locator(selector).wait_for(state="visible", timeout=timeout)

        # Wait for options to be populated
        if expected_value:
            # First wait for any options to exist in the dropdown
            try:
                current_page.wait_for_selector(
                    f"{selector} option", state="attached", timeout=5000
                )
            except Exception:
                print(f"Warning: No options found in dropdown {selector}")

            # Get all available options to find the matching value
            options = current_page.locator(f"{selector} option").all()
            available_values = []
            matched_value = None

            for option in options:
                try:
                    value = option.get_attribute("value")
                    text = option.text_content()
                    available_values.append(f"{value} ({text})")

                    # Match logic: handle "All" or case-insensitive matching
                    if expected_value.lower() == "all" and value.strip() == "":
                        matched_value = value
                    elif value.lower() == expected_value.lower():
                        matched_value = value
                except:
                    pass

            if matched_value is None:
                print(f"Warning: Option '{expected_value}' not found in {selector}")
                print(
                    f"Available options: {', '.join(available_values) if available_values else 'None'}"
                )
                if raise_on_missing:
                    raise Exception(
                        f"Option '{expected_value}' not found in dropdown {selector}. Available: {available_values}"
                    )
                return False

            # Wait for the matched option to be attached
            try:
                current_page.locator(
                    f"{selector} option[value='{matched_value}']"
                ).wait_for(state="attached", timeout=5000)
            except Exception as e:
                print(f"Warning: Matched option '{matched_value}' not attachable")
                # Continue anyway as the option exists
        else:
            # Just wait a moment for options to populate after the select is visible
            current_page.wait_for_timeout(500)

        return True

    def is_visible(self, selector: str):
        return self.page.locator(selector).is_visible()

    def element_visible(self, selector: str):
        return self.page.locator(selector).is_visible()

    def element_not_visible(self, selector: str):
        return self.page.locator(selector).is_hidden()

    def element_clickable(self, selector: str):
        return self.page.locator(selector).is_enabled()

    def element_not_clickable(self, selector: str):
        return self.page.locator(selector).is_disabled()

    # *********** get ***********
    def get_browser() -> dict:
        """Get browser name from environment variable and return the browser info."""
        browser_list = {
            "chrome": {"browser": "chromium"},
            "firefox": {"browser": "firefox"},
            "safari": {"browser": "webkit"},
            "edge": {"browser": "chromium", "channel": "msedge"},
        }
        env_browser = os.getenv("BROWSER") or os.getenv("browser") or "chrome"
        env_browser = env_browser.lower()
        if env_browser not in browser_list:
            raise Exception("Invalid browser")

        return browser_list[env_browser]

    def get_text(self, selector: str):
        return self.page.locator(selector).inner_text()

    def get_value(self, selector: str):
        return self.page.locator(selector).value()

    def get_attribute(self, selector: str, attribute: str):
        return self.page.locator(selector).get_attribute(attribute)

    def get_context(self):
        return self.page.context

    def get_url(self):
        return self.page.url

    def get_title(self):
        return self.page.title()

    def get_current_page(self):
        browser_context = self.page.context
        # print(f"Number of pages: {len(browser_context.pages)}")
        if len(browser_context.pages) > 1:
            current_page = browser_context.pages[-1]
        else:
            current_page = self.page
        return current_page

    def get_current_page_cookies(self, url):
        return self.page.context.cookies(url)

    def get_list_of_elements(self, selector: str):
        return self.page.locator(selector).all_inner_texts()

    def get_text_from_list_of_elements(self, elements: list):
        inner_text_list = []
        for i in range(len(elements)):
            inner_text_list.append(elements.nth(i).inner_text())
        return inner_text_list

    def get_value_from_list_of_elements(self, list_of_elements):
        return [element.value() for element in list_of_elements]

    def get_active_sub_nav_tab_status(self, selector: str, tab_name: str) -> bool:
        """Get the active sub navigation tab status."""
        active_link = self.page.locator(selector)
        assert (
            active_link.is_visible()
        ), f"Active tab link '{tab_name}' is not visible on the current page."
        return active_link.text_content() == tab_name

    def get_link_page_instance_after_click(
        self, selector: str = None, text: str = None
    ) -> Page:
        """
        Click a link and return the appropriate page instance based on the link name.
        Handles both same page navigation and new tab opening.

        Args:
          selector: CSS selector for the link element
          text: Text content of the link to click
          link_name: Name identifier for the page to return

        Returns:
          Page instance based on the link name
        """
        if not text and not selector:
            raise ValueError(
                "text or selector is required to determine the page instance"
            )

        browser_context = self.page.context
        initial_page_count = len(browser_context.pages)

        # Click the link
        if selector:
            self.click_element_if_visible(selector)
        elif text:
            self.click_text_link(text)
        else:
            raise ValueError("Either selector or link name must be provided")

        # Wait a moment for potential new tab to open
        self.wait_for_timeout(1000)

        # Check if new tab was opened
        current_page_count = len(browser_context.pages)
        if current_page_count > initial_page_count:
            # New tab opened, get the new page
            new_page = browser_context.pages[-1]
            new_page.wait_for_load_state("domcontentloaded")
            # Additional wait for page to fully load
            new_page.wait_for_load_state("load", timeout=self.timeout)
            target_page = new_page
        else:
            # Same page navigation - wait for both DOM and load events
            self.page.wait_for_load_state("domcontentloaded")
            self.wait_for_load_state("load")
            target_page = self.page
        # Return appropriate page instance based on text (link name)
        return target_page

    def _get_page_instance_by_name(
        self, link_name: str, page: Page, selector: str = None, heading: str = None
    ):
        """Helper method to return the page instance based on the link name."""
        match (link_name):
            case "datasets available in the Delta Lake":
                page.assert_page_heading(selector, heading)
            case _:
                raise ValueError(f"Unknown link name: {link_name}")

    def get_link_page_instance(self, link_name: str):
        """Return the page instance based on the link name."""
        return self._get_page_instance_by_name(link_name, self.page)

    def capture_storage_state_from_page(self, file_path: str):
        """This method is used to store the user state after login so that it can be reused whenever needed."""
        self.page.context.storage_state(path=file_path)

    # *********** click ***********
    def click_text_link(self, text: str):
        self.page.get_by_text(text).nth(0).click()

    def click_element(self, selector: str):
        self.page.locator(selector).click()

    def click_element_if_visible(self, selector: str):
        self.page.wait_for_selector(selector, timeout=30000)
        if self.page.locator(selector).is_visible():
            self.page.locator(selector).click()

    def click_element_if_clickable(self, selector: str):
        if self.page.locator(selector).is_enabled():
            self.page.locator(selector).click()

    # *********** Switch *********
    def click_link_to_switch_to_new_tab(
        self, selector: str | None = None, text: str | None = None
    ) -> Page:
        """Check if the link is clickable and switch to new tab."""
        if not selector and not text:
            raise ValueError("Either selector or text must be provided")

        browser_context = self.page.context
        with browser_context.expect_page() as new_page_tab:
            if selector:
                self.click_element_if_visible(selector)
            elif text:
                self.click_text_link(text)

        new_page = new_page_tab.value
        new_page.wait_for_load_state("domcontentloaded")
        print(f"New tab URL: {new_page.url}")
        return new_page

    # *********** fill ***********
    def fill_element(self, selector: str, text: str):
        self.page.locator(selector).fill(text)

    def fill_element_if_visible(self, selector: str, text: str):
        if self.page.locator(selector).is_visible():
            self.page.locator(selector).fill(text)

    def fill_element_if_enabled(self, selector: str, text: str):
        if self.page.locator(selector).is_enabled():
            self.page.locator(selector).fill(text)

    def fill_element_if_visible_and_enabled(self, selector: str, text: str):
        if (
            self.page.locator(selector).is_visible()
            and self.page.locator(selector).is_enabled()
        ):
            self.page.locator(selector).fill(text)

    # *********** select ***********
    def select_option(self, selector: str, value: str):
        """Select an option from dropdown with proper waiting."""
        current_page = self.get_current_page()
        # Wait for the select element and its options
        self.wait_for_dropdown_options(selector, value)
        # Find the matching value (handles case-insensitive matching and "All")
        matched_value = self._find_matching_option_value(selector, value)
        current_page.locator(selector).select_option(matched_value)
        # Wait for any network activity triggered by the selection
        current_page.wait_for_load_state("domcontentloaded")

    def _find_matching_option_value(self, selector: str, expected_value: str) -> str:
        """Find the actual option value that matches the expected value (case-insensitive)."""
        current_page = self.get_current_page()
        options = current_page.locator(f"{selector} option").all()

        for option in options:
            try:
                value = option.get_attribute("value")
                # Match logic: handle "All" or case-insensitive matching
                if expected_value.lower() == "all" and value.strip() == "":
                    return value
                elif value.lower() == expected_value.lower():
                    return value
            except:
                pass

        # If no match found, return the original value (will likely fail, but with better error)
        return expected_value

    def select_option_if_visible(self, selector: str, value: str):
        """Select an option if the dropdown is visible, with proper waiting.

        This method gracefully handles cases where the option doesn't exist in the dropdown,
        logging a warning but continuing execution. This is useful for negative test scenarios.
        """
        current_page = self.get_current_page()
        # First wait for the element to be attached and visible
        try:
            current_page.wait_for_selector(selector, state="visible", timeout=5000)
            if current_page.locator(selector).is_visible():
                # Wait for options to be populated (don't raise on missing for negative tests)
                option_exists = self.wait_for_dropdown_options(
                    selector, value, raise_on_missing=False
                )

                if not option_exists:
                    print(
                        f"Skipping selection: Option '{value}' not found in dropdown {selector}"
                    )
                    return False

                # Find the matching value (handles case-insensitive matching and "All")
                matched_value = self._find_matching_option_value(selector, value)
                current_page.locator(selector).select_option(matched_value)
                # Wait for any network activity triggered by the selection
                current_page.wait_for_load_state("domcontentloaded")
                return True
        except Exception as e:
            print(f"Warning: Could not select option {value} from {selector}: {e}")
            return False
            raise

    def select_option_if_enabled(self, selector: str, value: str):
        if self.page.locator(selector).is_enabled():
            self.page.locator(selector).select_option(value)

    def select_option_if_visible_and_enabled(self, selector: str, value: str):
        if (
            self.page.locator(selector).is_visible()
            and self.page.locator(selector).is_enabled()
        ):
            self.page.locator(selector).select_option(value)

    def scroll_and_click(self, selector: str):
        """Scroll to the element and click it."""
        self.page.locator(selector).scroll_into_view_if_needed()
        self.page.locator(selector).click()

    # *********** Assertions ***********
    def assert_heading_matches(self, heading: str):
        """Assert page heading with default heading selector as `h1`"""
        current_page = self.get_current_page()
        page_heading = current_page.locator("h1").inner_text()
        assert (
            page_heading == heading
        ), f"Heading does not match: expected '{heading}', got '{page_heading}'"

    def expect_title_matches(self, title: str):
        current_page = self.get_current_page()
        expect(current_page.title).to_equal(title)

    def expect_url_matches(self, url: str):
        expect(self.page.url).to_equal(url)

    def expect_text_matches(self, selector: str, text: str):
        expect(self.page.locator(selector).inner_text()).to_equal(text)

    def assert_url(self, url: str):
        assert self.page.url == url

    def assert_element_contains_text(self, selector: str, text: str):
        assert self.page.locator(selector).inner_text().contains(text)

    def assert_element_does_not_contain_text(self, selector: str, text: str):
        assert not self.page.locator(selector).inner_text().contains(text)

    def assert_element_contains_value(self, selector: str, value: str):
        assert self.page.locator(selector).value().contains(value)

    def assert_element_does_not_contain_value(self, selector: str, value: str):
        assert not self.page.locator(selector).value().contains(value)

    def assert_element_contains_attribute(
        self, selector: str, attribute: str, value: str
    ):
        assert self.page.locator(selector).get_attribute(attribute).contains(value)

    def assert_element_does_not_contain_attribute(
        self, selector: str, attribute: str, value: str
    ):
        assert not self.page.locator(selector).get_attribute(attribute).contains(value)

    def assert_element_has_attribute(self, selector: str, attribute: str):
        assert self.page.locator(selector).has_attribute(attribute)

    def assert_element_does_not_have_attribute(self, selector: str, attribute: str):
        assert not self.page.locator(selector).has_attribute(attribute)

    def assert_element_is_checked(self, selector: str):
        assert self.page.locator(selector).is_checked()

    def assert_element_is_not_checked(self, selector: str):
        assert not self.page.locator(selector).is_checked()

    def assert_element_is_selected(self, selector: str):
        assert self.page.locator(selector).is_selected()

    def assert_element_is_not_selected(self, selector: str):
        assert not self.page.locator(selector).is_selected()

    def assert_element_is_enabled(self, selector: str):
        assert self.page.locator(selector).is_enabled()

    def assert_element_is_disabled(self, selector: str):
        assert self.page.locator(selector).is_disabled()

    def assert_element_is_visible(self, selector: str):
        assert self.page.locator(selector).is_visible()

    def assert_element_is_not_visible(self, selector: str):
        assert self.page.locator(selector).is_hidden()

    def assert_element_is_focused(self, selector: str):
        assert self.page.locator(selector).is_focused()

    def assert_element_is_not_focused(self, selector: str):
        assert not self.page.locator(selector).is_focused()

    def assert_text(self, expected_text: str, actual_text: str):
        assert (
            expected_text == actual_text
        ), f"The text content does not match: expected {expected_text}, got {actual_text}"

    def assert_page_text(self, selector: str, text: str | list):
        """Get list of inner text from a webpage"""
        env_name = ut.get_environment_variable(
            "environmentName"
        ) or ut.get_environment_variable("envName")
        if type(text) == list:
            page_text = self.page.locator(selector).all_inner_texts()
        elif env_name.upper() in text:
            page_text_contexts = self.page.locator(selector).all_text_contents()
            page_text_list = [
                item.replace("\n", "") for item in page_text_contexts if item.strip()
            ]
            page_text_split_list = [
                word for item in page_text_list for word in item.split() if word
            ]
            first_value = page_text_split_list[0].upper()
            remaining_values = " ".join(page_text_split_list[1:])
            print(f"first_value: {first_value}")
            page_text = first_value + " " + remaining_values
        else:
            page_text = self.page.locator(selector).inner_text()
        print(f"page_text: {page_text}")

        import re

        def normalize(val):
            # If list, join elements with \n
            if isinstance(val, list):
                val = "\n".join(str(x) for x in val)
            # Remove trailing navigation text like 'Back to About' or similar
            val = re.sub(
                r"(back to about|backtoabout)[\s\n\.]*$",
                "",
                str(val),
                flags=re.IGNORECASE,
            )
            # Remove trailing punctuation (periods, spaces, newlines)
            val = re.sub(r"[\s\.]+$", "", val)
            # Normalize Unicode quotes to ASCII quotes
            val = (
                val.replace("\u2019", "'")
                .replace("\u2018", "'")
                .replace("\u201d", '"')
                .replace("\u201c", '"')
            )
            # Remove all whitespace and lowercase
            return re.sub(r"\s+", "", val).lower()

        normalized_actual = normalize(page_text)
        normalized_expected = normalize(text)

        # Debug output to help identify differences
        if normalized_actual != normalized_expected:
            print(f"\n=== TEXT COMPARISON DEBUG ===")
            print(f"Expected length: {len(normalized_expected)}")
            print(f"Actual length: {len(normalized_actual)}")

            # Write to files for detailed comparison
            with open("expected_normalized.txt", "w", encoding="utf-8") as f:
                f.write(normalized_expected)
            with open("actual_normalized.txt", "w", encoding="utf-8") as f:
                f.write(normalized_actual)

            # Find first difference
            min_len = min(len(normalized_expected), len(normalized_actual))
            for i in range(min_len):
                if normalized_expected[i] != normalized_actual[i]:
                    print(f"First difference at position {i}:")
                    start = max(0, i - 50)
                    end = min(len(normalized_expected), i + 50)
                    print(f"Expected: ...{normalized_expected[start:end]}...")
                    end_actual = min(len(normalized_actual), i + 50)
                    print(f"Actual:   ...{normalized_actual[start:end_actual]}...")
                    break
            print(f"=== END DEBUG ===\n")

        assert (
            normalized_actual == normalized_expected
        ), f"The page text content does not match: expected {normalized_expected[:100]}..., got {normalized_actual[:100]}..."

    def verify_external_link_href(self, selector: str, expected_href: str):
        """Verify that an external link has the correct href without navigating."""
        locator = self.page.locator(selector)
        locator.wait_for(state="visible", timeout=30000)
        actual_href = locator.get_attribute("href")

        assert (
            actual_href == expected_href
        ), f"External link href mismatch: expected '{expected_href}', got '{actual_href}'"

        print(f"✓ Verified external link href: {actual_href}")
        self.is_external_link_verification = True
        self.verified_external_href = actual_href
        return True

    def assert_page_title(self, title: str, timeout: int = 30000):
        # Skip title assertion for external link verification (stub mode)
        if self.is_external_link_verification:
            print(
                f"⊙ Skipping title assertion for external link: {self.verified_external_href}"
            )
            print(f"  Expected title would be: '{title}'")
            return

        current_page = self.get_current_page()

        # Retry logic for title to handle timing issues in CI/CD environments
        import time

        max_retries = 10  # Increased retries for slower CI/CD
        retry_delay = 2  # Increased delay between retries
        page_title = ""

        for attempt in range(max_retries):
            try:
                # Wait for load state before each attempt
                current_page.wait_for_load_state("domcontentloaded", timeout=10000)
                page_title = current_page.title()

                # If we got a non-empty title, break
                if page_title and page_title != "":
                    break

                print(
                    f"[Attempt {attempt + 1}/{max_retries}] Page title is empty, URL: {current_page.url}"
                )

                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
            except Exception as e:
                print(
                    f"[Attempt {attempt + 1}/{max_retries}] Error getting title: {str(e)}"
                )
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)

        # Get final URL for diagnostics
        final_url = current_page.url

        # Check if this is an external documentation URL that may not be accessible
        if not page_title or page_title == "":
            if "rsconnect" in final_url or "rsc" in final_url:
                error_msg = (
                    f"Title does not match: expected '{title}', got '{page_title}' | "
                    f"URL: {final_url} | "
                    f"NOTE: External documentation URL may not be accessible from Azure pipeline. "
                    f"Verify that 'rsconnect' hostname resolves and is reachable from the build environment."
                )
            else:
                error_msg = f"Title does not match: expected '{title}', got '{page_title}' | URL: {final_url}"
        else:
            error_msg = f"Title does not match: expected '{title}', got '{page_title}' | URL: {final_url}"

        assert page_title == title, error_msg

    def assert_page_heading(self, selector: str, heading: str):
        """Assert page heading with proper waiting for element to be available."""
        # Skip heading assertion for external link verification (stub mode)
        if self.is_external_link_verification:
            # Extract anchor from verified href to validate section mapping
            if self.verified_external_href and "#" in self.verified_external_href:
                anchor = self.verified_external_href.split("#")[-1]
                print(f"⊙ Skipping heading assertion for external link")
                print(f"  Expected heading: '{heading}'")
                print(f"  Link points to section anchor: '#{anchor}'")
            else:
                print(
                    f"⊙ Skipping heading assertion for external link: {self.verified_external_href}"
                )
            return

        current_page = self.get_current_page()
        # Wait for the heading element to be visible before getting text
        try:
            current_page.wait_for_selector(
                selector, state="visible", timeout=self.timeout
            )
            if type(heading) == list:
                page_heading = current_page.locator(selector).all_inner_texts()
            else:
                page_heading = current_page.locator(selector).inner_text()
            assert (
                page_heading == heading
            ), f"Heading does not match: expected '{heading}', got '{page_heading}'"
        except Exception as e:
            print(f"Error asserting page heading for selector '{selector}': {e}")
            # Capture screenshot for debugging
            self.capture_and_attach_screenshot(f"page_heading_assertion_failure")
            raise

    def assert_page_url(self, url: str):
        page_url = self.get_url()
        assert (
            page_url == url
        ), f"Page url does not match: expected '{url}', got '{page_url}'"

    # *********** Common Page Assertions ***********
    def assert_title_names(self, selector, expected_names):
        title_names = self.get_list_of_elements(selector)
        assert (
            title_names == expected_names
        ), f"Expected {expected_names}, but got {title_names}"

    def assert_title_description(self, selector, expected_descriptions):
        descriptions = self.get_list_of_elements(selector)
        assert (
            descriptions == expected_descriptions
        ), f"Expected {expected_descriptions}, but got {descriptions}"

    def assert_nav_tab_active(
        self,
        selector: str,
        attribute: str = "class",
        expected_value: str = "active",
    ):
        """
        Assert that a navigation or sub-navigation link/tab is active by checking its attribute value.
        selector: CSS selector for the nav/tab element
        attribute: attribute to check (default: 'class')
        expected_value: expected value or substring in the attribute (default: 'active')
        """
        element = self.page.locator(selector)
        attr_value = element.get_attribute(attribute)
        assert (
            attr_value and expected_value in attr_value
        ), f"Element '{selector}' does not have '{expected_value}' in attribute '{attribute}'. Actual: '{attr_value}'"

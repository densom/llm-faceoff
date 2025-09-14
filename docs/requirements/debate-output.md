# Debate Output Format Requirements

This document specifies the requirements for debate transcript output formats in the LLM Faceoff system.

## Overview

The debate system must generate well-structured, readable transcripts that capture all relevant information from a debate session. The output system supports multiple formats (Markdown, JSON, HTML) with consistent data representation across all formats.

## General Requirements

### Data Completeness
- **MUST** include all debate session metadata
- **MUST** include complete participant information
- **MUST** include all messages in chronological order
- **MUST** include session statistics and performance metrics
- **MUST** preserve message timestamps and types
- **MUST** maintain data integrity across all formats

### Readability
- **MUST** provide clear visual hierarchy
- **MUST** distinguish between different participant roles
- **MUST** format content for easy interpretation
- **MUST** include proper section breaks and spacing
- **SHOULD** use consistent formatting conventions

## Markdown Format Requirements

### Document Structure
The markdown output **MUST** follow this hierarchical structure:

1. **Title Section**
   - Main title with debate topic
   - Debate information table

2. **Participants Section**
   - Individual participant subsections
   - Role, provider, and model information

3. **Rules Section** (if applicable)
   - Debate-specific rules and constraints
   - Only included when session has configured rules

4. **Transcript Section**
   - Chronological message sequence
   - Turn-based organization

5. **Summary Section**
   - Session statistics
   - Participant performance metrics
   - Status information

### Title Section Requirements
- **MUST** use H1 heading with topic as title
- **MUST** include debate format, status, and timing information
- **MUST** use markdown table for metadata display
- **SHOULD** use visual indicators (emojis) for enhanced readability

### Participant Section Requirements
- **MUST** list all debate participants
- **MUST** include participant name, role, provider, and model
- **MUST** use distinct visual indicators for different roles:
  - Proposition: ✅
  - Opposition: ❌
  - Moderator: ⚖️
- **MUST** use H3 headings for individual participants

### Rules Section Requirements
- **MUST** include Rules Section when `session.config.rules` contains non-empty values
- **MAY** omit Rules Section when no specific rules are configured for the debate
- **MUST** display rule keys and values in a clear, readable format
- **SHOULD** use bullet points or definition lists for rule presentation

### Transcript Section Requirements
- **MUST** organize messages by turn number in chronological order
- **MUST** number turns sequentially starting from 1, including moderator messages
- **MUST** clearly distinguish between moderator messages and participant debate messages
- **MUST** include participant identification for each message
- **MUST** display message type and timestamp
- **MUST** support the following message types:
  - Moderator Comment
  - Opening Statement
  - Argument
  - Rebuttal
  - Closing Statement
- **MUST** preserve original message content
- **MUST** use horizontal rules (`---`) between messages
- **MUST** format content with proper line breaks and punctuation
- **MAY** automatically append terminal punctuation to content that lacks proper sentence ending
- **SHOULD** handle empty or missing content gracefully

### Summary Section Requirements
- **MUST** include overview statistics table with:
  - Total messages count
  - Total participants count
  - Debate duration
  - Average message length
- **MUST** include individual participant performance metrics:
  - Message count per participant
  - Total character count per participant
  - Average character count per participant
- **MUST** display current debate status
- **MUST** include generation timestamp
- **MUST** use thousands separators for large numbers in statistics (e.g., "7,264")
- **SHOULD** use tables for organized data display

### Formatting Standards
- **MUST** use proper markdown syntax
- **MUST** use actual newlines in generated markdown, but **MAY** preserve escaped newlines from source content when appropriate
- **MUST** maintain consistent spacing between sections
- **MUST** use bold formatting for field labels
- **MUST** use italics for status messages and metadata
- **SHOULD** use emojis consistently for visual enhancement

## JSON Format Requirements

### Schema Requirements
The JSON output **MUST** include these top-level fields:

- `session_id`: Unique session identifier
- `config`: Complete debate configuration
- `participants`: Array of participant objects
- `status`: Current session status
- `created_at`: Session creation timestamp
- `started_at`: Session start timestamp (nullable)
- `completed_at`: Session completion timestamp (nullable)
- `current_turn`: Current turn number
- `messages`: Array of message objects
- `statistics`: Computed session statistics

### Configuration Object
**MUST** include:
- `topic`: Debate topic string
- `format`: Debate format identifier
- `max_turns`: Maximum allowed turns
- `max_response_length`: Character limit per response
- `rules`: Object containing debate-specific rules

### Participant Objects
**MUST** include:
- `id`: Unique participant identifier
- `name`: Participant display name
- `provider`: LLM provider name
- `model`: Specific model identifier
- `role`: Participant role (proposition/opposition/moderator)

### Message Objects
**MUST** include:
- `id`: Unique message identifier
- `participant_id`: Reference to participant
- `content`: Message text content
- `type`: Message type identifier
- `timestamp`: ISO formatted timestamp
- `metadata`: Additional message metadata

### Statistics Object
**MUST** include:
- `total_messages`: Total message count
- `total_participants`: Total participant count
- `duration_minutes`: Session duration in minutes
- `avg_message_length`: Average message character count
- `participant_stats`: Per-participant statistics object

## HTML Format Requirements

### Document Structure
- **MUST** be valid HTML5 document
- **MUST** include proper DOCTYPE and meta tags
- **MUST** include embedded CSS for styling
- **MUST** use semantic HTML elements

### Styling Requirements
- **MUST** provide responsive design
- **MUST** use role-based color coding for participants
- **MUST** ensure readability across different screen sizes
- **MUST** include proper typography and spacing

### Content Requirements
- **MUST** include all information present in markdown format
- **MUST** escape HTML special characters in content
- **MUST** maintain chronological message ordering
- **MUST** provide clear visual separation between sections

## Error Handling Requirements

### Missing Data
- **MUST** handle missing participant names gracefully
- **MUST** use `{provider}-{model}` format as fallback when participant name is missing or "Unnamed"
- **MUST** provide default values for optional fields
- **MUST** display appropriate placeholders for null timestamps
- **SHOULD** indicate incomplete or missing information clearly

### Content Validation
- **MUST** handle empty message content
- **MUST** validate timestamp formats
- **MUST** ensure participant references are valid
- **SHOULD** provide meaningful error messages for invalid data

## Performance Requirements

### Generation Speed
- **SHOULD** generate transcripts efficiently for sessions with up to 100 messages
- **SHOULD** handle large content without significant performance degradation

### Memory Usage
- **SHOULD** maintain reasonable memory footprint during generation
- **SHOULD** stream output for very large sessions when possible

## Compatibility Requirements

### File Format
- **MUST** generate UTF-8 encoded output
- **MUST** use appropriate file extensions (.md, .json, .html)
- **MUST** ensure cross-platform compatibility

### File Naming Convention
- **MUST** follow the pattern: `debate_{timestamp}_{topic_slug}.{extension}`
  - `{timestamp}`: Session creation time in format `YYYYMMDD_HHMMSS`
  - `{topic_slug}`: Sanitized debate topic (alphanumeric characters only, others replaced with underscores)
  - `{extension}`: Format-specific extension (md, json, html)
- **MUST** limit topic slug to first 50 characters of the debate topic
- **MUST** sanitize topic by replacing non-alphanumeric characters with underscores
- **MUST** use consistent naming across all output formats for the same session

### Markdown Compatibility
- **MUST** generate CommonMark compliant markdown
- **SHOULD** be compatible with popular markdown renderers
- **SHOULD** render correctly in GitHub, VS Code, and other common viewers

## Future Considerations

### Extensibility
- **SHOULD** support additional output formats through plugin architecture
- **SHOULD** allow customization of formatting templates
- **SHOULD** support internationalization for UI text

### Analytics Integration
- **SHOULD** provide hooks for additional statistics calculation
- **SHOULD** support custom metadata fields
- **SHOULD** enable integration with external analysis tools

---

*Document Version: 1.0*
*Last Updated: September 2025*